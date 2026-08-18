import os
import json
from typing import Dict, Any, List
import requests
from ai.vector_store import MovieVectorStore
from ai.prompt_templates import rag_prompt
from dotenv import load_dotenv

load_dotenv()

class RAGPipeline:
    def __init__(self):
        self.vector_store = None
        self.movie_lookup = {}
        self.is_initialized = False

    def initialize(self):
        if self.is_initialized:
            return

        print("Initializing RAG Pipeline...")
        # 1. Initialize Vector Store
        try:
            self.vector_store = MovieVectorStore()
        except Exception as e:
            print(f"Failed to initialize Vector Store: {e}")
            self.vector_store = None

        # 3. Load Fact Lookup Data for Grounding
        self._load_movie_lookup()
        
        self.is_initialized = True

    def _load_movie_lookup(self):
        """Load the authoritative JSON lookup for O(1) fact checking."""
        lookup_path = "data/processed/movie_lookup.json"
        if not os.path.exists(lookup_path):
            print(f"Warning: {lookup_path} not found. Grounding might be limited.")
            return

        try:
            with open(lookup_path, "r", encoding="utf-8") as f:
                self.movie_lookup = json.load(f)
            print(f"Loaded {len(self.movie_lookup)} movie facts into memory.")
        except Exception as e:
            print(f"Error loading movie lookup: {e}")

    def _build_context(self, candidates: List[Dict[str, Any]]) -> str:
        """Construct a strictly grounded string of movie facts."""
        context_parts = []
        for cand in candidates:
            movie_id = str(cand["movie_id"])
            
            # Prefer facts from the O(1) lookup dictionary
            facts = self.movie_lookup.get(movie_id, cand.get("metadata", {}))
            
            title = facts.get("title", cand["title"])
            overview = facts.get("overview", facts.get("content", "No description available."))
            genres = facts.get("genres", facts.get("genre_text", "Unknown"))
            cast = facts.get("cast", facts.get("people_text", "Unknown"))
            rating = facts.get("vote_average", facts.get("rating_score", "Unknown"))
            year = facts.get("release_year", facts.get("year_bucket", "Unknown"))
            
            movie_str = (
                f"ID: {movie_id} | Title: {title} ({year})\n"
                f"Genres: {genres} | Rating: {rating}/10\n"
                f"Cast/Crew: {cast}\n"
                f"Plot: {overview}\n"
                f"Similarity Score: {cand['score']:.4f}\n"
            )
            context_parts.append(movie_str)
            
        return "\n---\n".join(context_parts)

    def _call_llama(self, prompt: str) -> str:
        hf_token = os.getenv("HF_TOKEN")
        hf_model = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
        hf_provider = os.getenv("HF_PROVIDER", "auto")
        
        if not hf_token:
            return "Error: HF_TOKEN is not set."

        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(provider=hf_provider, api_key=hf_token)
            
            completion = client.chat.completions.create(
                model=hf_model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI movie recommendation assistant. Be brief and friendly."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=int(os.getenv("HF_MAX_TOKENS", "1024")),
                temperature=0.7,
            )
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            return f"HuggingFace API Error: {e}"

    def generate_recommendation(self, user_query: str, top_k: int = 5) -> str:
        """
        End-to-end RAG workflow:
        1. Query processing
        2. Vector retrieval
        3. Context grounding
        4. LLM Generation
        """
        if not user_query or not user_query.strip():
            return "Please provide a valid query."

        if not self.is_initialized:
            self.initialize()

        if not self.vector_store:
            return "Error: Vector database is not configured or unavailable."

        # 1. Semantic Retrieval
        print(f"Searching Pinecone for: '{user_query}'...")
        try:
            candidates = self.vector_store.search_movies(user_query, top_k=top_k)
        except Exception as e:
            print(f"Retrieval Error: {e}")
            return "I'm having trouble searching the movie database right now."

        if not candidates:
            return "I couldn't find movies that closely match that request in the available catalog."

        # 2. Context Grounding
        context = self._build_context(candidates)

        # 3. LLM Generation
        # Build prompt
        prompt = rag_prompt.format(user_query=user_query, context=context)

        # Call Llama 3.1
        print("Generating explanation with Llama 3.1...")
        response_text = self._call_llama(prompt)
        
        # If there's a DNS/Network error, fallback to displaying the Pinecone results nicely
        if "Error contacting HuggingFace API" in response_text or "HuggingFace API Error" in response_text:
            fallback = "I'm having trouble connecting to my language generator (network issue), but here are the best matches I found for you:\n\n"
            for c in candidates:
                fallback += f"- **{c['title']}** (Score: {c['score']:.2f})\n"
                fallback += f"  *Plot:* {self.movie_lookup.get(str(c['movie_id']), c.get('metadata', {})).get('overview', 'No plot available')[:100]}...\n\n"
            return fallback
            
        return response_text.strip()

# Singleton instance
rag_pipeline_instance = RAGPipeline()
