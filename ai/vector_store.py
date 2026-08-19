import os
from typing import List, Dict, Any
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

class MovieVectorStore:
    def __init__(self):
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "movie-recommendations")
        
        self.index = None
        self.model = None

        if pinecone_api_key:
            try:
                print(f"Connecting to Pinecone index '{self.index_name}'...")
                pc = Pinecone(api_key=pinecone_api_key)
                self.index = pc.Index(self.index_name)
            except Exception as e:
                print(f"Pinecone initialization note: {e}")

        try:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"SentenceTransformer initialization note: {e}")

    def search_movies(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.index or not self.model:
            return []

        try:
            query_vector = self.model.encode(query).tolist()
            res = self.index.query(vector=query_vector, top_k=top_k, include_metadata=True)

            candidates = []
            for match in res.get("matches", []):
                meta = match.get("metadata", {})
                candidates.append({
                    "movie_id": meta.get("movie_id"),
                    "title": meta.get("title", "Unknown Title"),
                    "score": match.get("score", 0.0),
                    "content": meta.get("content", ""),
                    "metadata": meta
                })
            return candidates
        except Exception as e:
            print(f"Vector search error: {e}")
            return []
