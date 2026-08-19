import os
from ai.vector_store import MovieVectorStore
from ai.rag_pipeline import rag_pipeline_instance
from dotenv import load_dotenv

load_dotenv()

# Test 1: Vector Store Initialization
print("Test 1: Vector Store Init")
vs = MovieVectorStore()
emb = vs.embeddings.embed_query("dark psychological sci-fi")
print("Embedding loaded successfully")
print("Dimension:", len(emb))

# Test 2: RAG Pipeline Generation
print("\nTest 2: RAG Pipeline Generation")
os.environ["HF_SSL_VERIFY"] = "false"
response = rag_pipeline_instance.generate_recommendation("Recommend me dark sci-fi movies similar to Interstellar")
print("\nGenerated Response:\n")
print(response)
