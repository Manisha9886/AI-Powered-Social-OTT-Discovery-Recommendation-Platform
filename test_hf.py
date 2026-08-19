import os
os.environ["HF_HUB_OFFLINE"] = "1"
from sentence_transformers import SentenceTransformer
import time

start = time.time()
try:
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embedding = model.encode("dark psychological sci-fi")
    print("Embedding loaded successfully")
    print("Dimension:", len(embedding))
    print("Time taken:", time.time() - start)
except Exception as e:
    print("Error:", e)
