import os
from typing import List, Dict, Any
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

class MovieVectorStore:
    def __init__(self):
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "movie-recommendations")
        
        if not pinecone_api_key:
            raise ValueError("PINECONE_API_KEY environment variable is not set.")

        # SSL bypass flag for development
        verify_ssl = os.getenv("HF_SSL_VERIFY", "true").lower() == "true"

        print(f"Connecting to Pinecone index '{self.index_name}'...")
        # Initialize Pinecone
        pc = Pinecone(api_key=pinecone_api_key, ssl_verify=verify_ssl)
        self.index = pc.Index(self.index_name)
        
        # We must use the exact same model that generated the embeddings
        # (all-MiniLM-L6-v2 produces 384-dimensional vectors)
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"local_files_only": True}
        )
        
        self.vector_store = PineconeVectorStore(
            index=self.index,
            embedding=self.embeddings,
            text_key="content" # This is the field in metadata containing the text
        )

    def search_movies(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a semantic similarity search in Pinecone.
        Returns the top_k most similar movie documents.
        """
        # We use similarity_search_with_score to get the confidence
        results = self.vector_store.similarity_search_with_score(query, k=top_k)
        
        candidates = []
        for doc, score in results:
            candidates.append({
                "movie_id": doc.metadata.get("movie_id"),
                "title": doc.metadata.get("title", "Unknown Title"),
                "score": score,
                "content": doc.page_content,
                "metadata": doc.metadata
            })
            
        return candidates
