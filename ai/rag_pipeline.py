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
        self.bm25_index = None
        self.bm25_corpus_map = []
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

        # 2. Load Fact Lookup Data for Grounding
        self._load_movie_lookup()
        
        # 3. Build Local BM25 Sparse Index
        self._build_bm25_index()

        self.is_initialized = True

        print("Pinecone Dense Retrieval: READY")
        if self.bm25_index:
            print("BM25 Sparse Retrieval: READY")
            print("Hybrid RRF Retrieval: READY")
        else:
            print("BM25 Sparse Retrieval: UNAVAILABLE")

    def _load_movie_lookup(self):
        """Load the authoritative JSON lookup for O(1) fact checking."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        lookup_path = os.path.join(base_dir, "data", "processed", "movie_lookup.json")
        if not os.path.exists(lookup_path):
            print(f"Warning: {lookup_path} not found. Grounding might be limited.")
            return

        try:
            with open(lookup_path, "r", encoding="utf-8") as f:
                self.movie_lookup = json.load(f)
            print(f"Loaded {len(self.movie_lookup)} movie facts into memory.")
        except Exception as e:
            print(f"Error loading movie lookup: {e}")

    def _tokenize(self, text: str) -> List[str]:
        """Simple deterministic tokenizer: lowercase, remove punctuation, split by whitespace."""
        import string
        text = text.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))
        return text.split()

    def _expand_query(self, user_query: str) -> str:
        """
        Expands natural language terms with catalog standard genres and keywords.
        For example: 'funny' -> 'funny comedy laugh hilarious'
        """
        synonym_map = {
            "funny": "comedy laugh hilarious",
            "hilarious": "comedy funny laugh",
            "humorous": "comedy funny",
            "laugh": "comedy funny",
            "scary": "horror frightening spooky creepy",
            "spooky": "horror scary",
            "creepy": "horror scary",
            "frightening": "horror scary",
            "romantic": "romance love dating",
            "love": "romance romantic",
            "action-packed": "action adventure explosive",
            "sci-fi": "science fiction scifi futuristic space",
            "scifi": "science fiction scifi futuristic space",
            "futuristic": "science fiction scifi",
            "space": "science fiction space",
            "thriller": "thriller suspense mystery edge-of-seat",
            "suspense": "thriller suspense mystery",
            "mystery": "mystery thriller detective",
            "animated": "animation animated cartoon",
            "cartoon": "animation animated",
            "anime": "animation anime japanese",
            "kids": "family children kids",
            "children": "family children kids",
            "family": "family children kids",
            "emotional": "drama emotional tearjerker",
            "sad": "drama emotional",
        }
        
        query_words = self._tokenize(user_query)
        expanded_terms = set(query_words)
        
        for word in query_words:
            if word in synonym_map:
                for syn in synonym_map[word].split():
                    expanded_terms.add(syn)
                    
        expanded_query = " ".join(expanded_terms)
        return expanded_query if expanded_query.strip() else user_query


    def _build_bm25_index(self):
        """Builds a local BM25 sparse index using available metadata fields."""
        if not self.movie_lookup:
            print("Warning: movie_lookup is empty. Cannot build BM25 index.")
            return

        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            print("Warning: rank_bm25 not installed. Using dense retrieval fallback.")
            return

        print("Building BM25 sparse index from movie corpus...")
        tokenized_corpus = []
        self.bm25_corpus_map = []

        for movie_id_str, movie_data in self.movie_lookup.items():
            # Combine relevant fields
            title = movie_data.get("title", "")
            overview = movie_data.get("overview", movie_data.get("content", ""))
            genres = " ".join(movie_data.get("genres", []) if isinstance(movie_data.get("genres"), list) else [movie_data.get("genres", "")])
            cast = " ".join(movie_data.get("cast", []) if isinstance(movie_data.get("cast"), list) else [movie_data.get("cast", "")])
            keywords = " ".join(movie_data.get("keywords", []) if isinstance(movie_data.get("keywords"), list) else [movie_data.get("keywords", "")])

            # Construct searchable document
            searchable_text = f"{title} {genres} {overview} {overview} {keywords} {cast}"
            
            tokenized_corpus.append(self._tokenize(searchable_text))
            self.bm25_corpus_map.append({
                "movie_id": int(movie_id_str),
                "title": title,
                "metadata": movie_data
            })

        try:
            self.bm25_index = BM25Okapi(tokenized_corpus)
            print(f"BM25 index built with {len(self.bm25_corpus_map)} documents.")
        except Exception as e:
            print(f"Error initializing BM25: {e}")
            self.bm25_index = None

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
        
        if not hf_token:
            return "Error: HF_TOKEN is not set."

        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(model=hf_model, token=hf_token)
            
            messages = [
                {"role": "system", "content": "You are a helpful AI movie recommendation assistant. Be brief and friendly."},
                {"role": "user", "content": prompt}
            ]
            max_tokens = int(os.getenv("HF_MAX_TOKENS", "1024"))
            
            response = client.chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
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

        # 1. Retrieval
        expanded_query = self._expand_query(user_query)
        print(f"Executing Hybrid Search (Dense on raw query, Sparse on expanded query: '{expanded_query}')...")
        
        # Dense Retrieval (Pinecone - query with original semantic query)
        dense_candidates = []
        try:
            # Fetch more candidates for fusion using semantic embedding
            dense_candidates = self.vector_store.search_movies(user_query, top_k=20)
        except Exception as e:
            print(f"Dense Retrieval Error: {e}")
            if not self.bm25_index:
                return "I'm having trouble searching the movie database right now."

        # Sparse Retrieval (BM25 - query with expanded keywords)
        sparse_candidates = []
        if self.bm25_index:
            try:
                tokenized_query = self._tokenize(expanded_query)
                bm25_scores = self.bm25_index.get_scores(tokenized_query)
                
                # Get top 20
                import numpy as np
                top_sparse_idx = np.argsort(bm25_scores)[::-1][:20]
                
                for idx in top_sparse_idx:
                    if bm25_scores[idx] > 0:
                        doc = self.bm25_corpus_map[idx]
                        sparse_candidates.append({
                            "movie_id": doc["movie_id"],
                            "title": doc["title"],
                            "score": float(bm25_scores[idx]),
                            "metadata": doc["metadata"]
                        })
            except Exception as e:
                print(f"Sparse Retrieval Error: {e}")

        # Reciprocal Rank Fusion (RRF with Dense Vector Priority)
        rrf_scores = {}
        candidate_docs = {}
        k = 60 # Standard RRF constant
        
        dense_weight = 2.5   # Emphasize semantic vector search
        sparse_weight = 0.5  # De-emphasize exact keyword matches
        
        # Rank 1-indexed
        for rank, cand in enumerate(dense_candidates, start=1):
            mid = cand["movie_id"]
            rrf_scores[mid] = rrf_scores.get(mid, 0) + (dense_weight / (rank + k))
            cand["dense_score"] = cand.get("score")
            candidate_docs[mid] = cand
            
        for rank, cand in enumerate(sparse_candidates, start=1):
            mid = cand["movie_id"]
            rrf_scores[mid] = rrf_scores.get(mid, 0) + (sparse_weight / (rank + k))
            if mid not in candidate_docs:
                candidate_docs[mid] = cand
            candidate_docs[mid]["bm25_score"] = cand.get("score")


        # Sort by RRF score
        fused_candidates = []
        for mid, rrf_score in sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True):
            doc = candidate_docs[mid]
            doc["rrf_score"] = rrf_score
            doc["score"] = rrf_score # Override score for downstream context builder
            fused_candidates.append(doc)
            
        candidates = fused_candidates[:top_k]
        print(f"Hybrid Retrieval Complete: {len(dense_candidates)} dense, {len(sparse_candidates)} sparse -> {len(candidates)} fused returned.")

        if not candidates:
            print("No hybrid search candidates found. Utilizing top catalog candidates as fallback...")
            fallback_candidates = []
            for movie_id_str, movie_data in self.movie_lookup.items():
                rating = float(movie_data.get("vote_average", 0) or 0)
                fallback_candidates.append({
                    "movie_id": int(movie_id_str),
                    "title": movie_data.get("title", "Unknown"),
                    "score": rating,
                    "metadata": movie_data
                })
            fallback_candidates.sort(key=lambda x: x["score"], reverse=True)
            candidates = fallback_candidates[:top_k]


        # 2. Context Grounding
        context = self._build_context(candidates)

        # 3. LLM Generation
        # Build prompt
        prompt = rag_prompt.format(user_query=user_query, context=context)

        # Call Llama 3.1
        print("Generating explanation with Llama 3.1...")
        response_text = self._call_llama(prompt)
        
        # If HF API returned an error, generate a grounded response directly from retrieved candidates
        if "HuggingFace API Error" in response_text or "Error:" in response_text or not response_text.strip():
            print("HF API fallback triggered. Generating context-grounded response directly...")
            recs_list = []
            for idx, cand in enumerate(candidates[:5], start=1):
                mid = str(cand["movie_id"])
                facts = self.movie_lookup.get(mid, cand.get("metadata", {}))
                title = facts.get("title", cand.get("title", "Movie"))
                year = facts.get("release_year", facts.get("year_bucket", "Unknown"))
                genres = facts.get("genres", facts.get("genre_text", "Unknown"))
                if isinstance(genres, list):
                    genres = ", ".join(genres)
                rating = facts.get("vote_average", facts.get("rating_score", "7.0"))
                
                rec_item = (
                    f"{idx}. {title} ({year})\n"
                    f"   Why it fits: Matches your request based on plot themes and catalog similarity.\n"
                    f"   Genre: {genres}\n"
                    f"   Rating: {rating}/10"
                )
                recs_list.append(rec_item)
                
            return f"Based on your request, here are top recommendations matching your query:\n\n" + "\n\n".join(recs_list)
            
        return response_text.strip()

    def explain_recommendation(self, movie_id: int, user_query: str, evidence: Dict[str, Any]) -> str:
        """
        Explain why a movie was recommended using Grounded LLM Explainability.
        This uses O(1) fact lookup for authoritative context rather than a redundant Pinecone search.
        """
        if not self.is_initialized:
            self.initialize()

        movie_id_str = str(movie_id)
        facts = self.movie_lookup.get(movie_id_str, {})
        
        title = facts.get("title", f"Movie ID {movie_id}")
        overview = facts.get("overview", "No plot available.")
        genres = facts.get("genres", "Unknown")
        year = facts.get("release_year", "Unknown")

        context = (
            f"Title: {title} ({year})\n"
            f"Genres: {genres}\n"
            f"Plot: {overview}\n"
        )

        evidence_str = json.dumps(evidence, indent=2)

        prompt = (
            "You are explaining a recommendation produced by a hybrid movie recommendation system.\n"
            f"Explain why the recommended movie '{title}' is a good match for the user.\n"
            "Use the supplied recommendation evidence and verified movie context below.\n"
            "Do not invent movie facts. Do not invent recommendation scores.\n"
            "Do not claim evidence that is not provided. If the evidence is insufficient, say so.\n"
            "Your response should be concise, natural and understandable to a user.\n"
            "Return PLAIN TEXT ONLY. Do NOT use Markdown, asterisks, bold formatting, or bullet points.\n\n"
            f"USER REQUEST: {user_query or 'General recommendation'}\n\n"
            f"RECOMMENDATION EVIDENCE:\n{evidence_str}\n\n"
            f"VERIFIED MOVIE CONTEXT:\n{context}\n\n"
            "EXPLANATION:"
        )

        print(f"Generating explanation for {movie_id} with Llama 3.1...")
        response_text = self._call_llama(prompt)
        
        if "HuggingFace API Error" in response_text or "Error:" in response_text or not response_text.strip():
            return f"'{title}' is recommended because its genre profile ({genres}) and ratings match your viewing preferences."
            
        return response_text.strip()

# Singleton instance
rag_pipeline_instance = RAGPipeline()
