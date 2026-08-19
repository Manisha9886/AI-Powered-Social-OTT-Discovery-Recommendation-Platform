import os
import json
import time
from typing import List, Dict, Any
import pandas as pd
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Load environment variables
load_dotenv()

# Clean up invalid SSL environment variables if file does not exist
for ssl_var in ["SSL_CERT_FILE", "REQUESTS_CA_BUNDLE"]:
    if ssl_var in os.environ and not os.path.exists(os.environ[ssl_var]):
        del os.environ[ssl_var]

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "movie-recommendations")
BATCH_SIZE = 100
EXPECTED_DIMENSION = 384

def load_data():
    print("Loading data...")
    # Load Parquet
    parquet_path = "data/processed/movie_embeddings.parquet"
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Missing {parquet_path}")
    df = pd.read_parquet(parquet_path)
    
    # Load JSON
    json_path = "data/processed/movie_knowledge_docs.json"
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Missing {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        knowledge_docs = json.load(f)
        
    return df, knowledge_docs

def prepare_records(df: pd.DataFrame, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    print("Preparing records...")
    # Create a lookup for docs by movie_id
    doc_lookup = {str(doc['movie_id']): doc for doc in docs}
    
    records = []
    
    for _, row in df.iterrows():
        movie_id = str(row['movie_id'])
        embedding = row['embedding'].tolist() if hasattr(row['embedding'], 'tolist') else list(row['embedding'])
        
        # Validation
        if len(embedding) != EXPECTED_DIMENSION:
            print(f"Warning: Movie {movie_id} has dimension {len(embedding)}. Skipping.")
            continue
            
        doc = doc_lookup.get(movie_id)
        if not doc:
            print(f"Warning: Missing knowledge doc for movie {movie_id}. Skipping.")
            continue
            
        # Build metadata (safely extract strings and basic types for Pinecone)
        metadata = {
            "movie_id": movie_id,
            "title": doc.get("title", ""),
            "content": doc.get("content", ""),
            # Extract basic metadata
        }
        
        # Add extra metadata if present and flat
        meta_dict = doc.get("metadata", {})
        for k, v in meta_dict.items():
            if isinstance(v, (str, int, float, bool)):
                metadata[k] = v
            elif isinstance(v, list) and all(isinstance(x, str) for x in v):
                # Pinecone supports list of strings
                metadata[k] = v
                
        records.append({
            "id": f"movie_{movie_id}",
            "values": embedding,
            "metadata": metadata
        })
        
    return records

def ingest_to_pinecone(records: List[Dict[str, Any]]):
    print(f"Connecting to Pinecone index: {PINECONE_INDEX_NAME}...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        print(f"Index {PINECONE_INDEX_NAME} not found! Please create it with dimension {EXPECTED_DIMENSION}.")
        return

    index = pc.Index(PINECONE_INDEX_NAME)
    
    print(f"Starting ingestion of {len(records)} vectors in batches of {BATCH_SIZE}...")
    total_batches = (len(records) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        
        # Retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                index.upsert(vectors=batch)
                print(f"Uploaded batch {batch_num}/{total_batches}")
                break
            except Exception as e:
                print(f"Error on batch {batch_num} (attempt {attempt+1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    print(f"Failed to upload batch {batch_num}. Skipping.")
                time.sleep(2 ** attempt) # Exponential backoff
                
    print(f"Successfully indexed {len(records)} vectors.")

def main():
    try:
        df, docs = load_data()
        records = prepare_records(df, docs)
        
        if not records:
            print("No valid records to ingest.")
            return
            
        print(f"Found {len(records)} valid movie vectors. Embedding dimension: {EXPECTED_DIMENSION}.")
        
        ingest_to_pinecone(records)
        
    except Exception as e:
        import traceback
        print(f"Ingestion failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
