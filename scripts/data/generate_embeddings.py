"""
Movie Embeddings & Semantic Vector Generation Script
=====================================================
Generates dense semantic embeddings for all movies in `movies_features.csv`
using the `all-MiniLM-L6-v2` Sentence-Transformer model on the `combined_text` column.

Inputs:
- data/processed/movies_features.csv

Outputs:
- data/processed/movie_embeddings.npy       (Dense numpy matrix: [N, 384])
- data/processed/movie_embeddings.parquet   (DataFrame with movie_id, title, embedding)
- data/processed/movie_embedding_ids.json   (Ordered list of movie_ids corresponding to rows in .npy)
- data/processed/embedding_report.txt       (Audit report)
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import pandas as pd

# Windows UTF-8 console output
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"

INPUT_FEATURES_FILE = PROCESSED_DIR / "movies_features.csv"
OUTPUT_EMBEDDINGS_NPY = PROCESSED_DIR / "movie_embeddings.npy"
OUTPUT_EMBEDDINGS_PARQUET = PROCESSED_DIR / "movie_embeddings.parquet"
OUTPUT_IDS_JSON = PROCESSED_DIR / "movie_embedding_ids.json"
OUTPUT_REPORT = PROCESSED_DIR / "embedding_report.txt"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 64


def generate_embeddings():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading movie features from: {INPUT_FEATURES_FILE}")
    movies_df = pd.read_csv(INPUT_FEATURES_FILE)
    total_movies = len(movies_df)
    print(f"Total movies to process: {total_movies:,}")

    # Prepare texts to embed
    # Fallback to title + overview if combined_text is somehow empty
    texts: List[str] = []
    for idx, row in movies_df.iterrows():
        ct = str(row["combined_text"]).strip() if pd.notna(row["combined_text"]) else ""
        if not ct:
            title = str(row["title"]).strip() if pd.notna(row["title"]) else "Unknown"
            overview = str(row["overview"]).strip() if pd.notna(row["overview"]) else ""
            ct = f"Title: {title}. Overview: {overview}"
        texts.append(ct)

    movie_ids = movies_df["movie_id"].tolist()
    movie_titles = movies_df["title"].tolist()

    print(f"\nLoading embedding model: {MODEL_NAME}...")
    start_time = time.time()
    model = SentenceTransformer(MODEL_NAME)
    
    print(f"Encoding {len(texts)} movies (batch size = {BATCH_SIZE})...")
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,  # Normalized vectors for fast cosine similarity via dot product
        convert_to_numpy=True
    )
    duration = time.time() - start_time
    
    embedding_dim = embeddings.shape[1]
    successful_count = len(embeddings)
    failed_count = total_movies - successful_count
    
    print(f"\nEncoding complete in {duration:.2f} seconds.")
    print(f"Embeddings shape: {embeddings.shape} (dim = {embedding_dim})")

    # 1. Save raw numpy array (.npy)
    np.save(OUTPUT_EMBEDDINGS_NPY, embeddings.astype(np.float32))
    print(f"Saved numpy embeddings to: {OUTPUT_EMBEDDINGS_NPY}")

    # 2. Save ordered movie ID index (.json)
    with open(OUTPUT_IDS_JSON, "w", encoding="utf-8") as f:
        json.dump(movie_ids, f)
    print(f"Saved movie IDs mapping to: {OUTPUT_IDS_JSON}")

    # 3. Save as Parquet with movie_id, title, and embedding list for direct table queries
    embeddings_df = pd.DataFrame({
        "movie_id": movie_ids,
        "title": movie_titles,
        "embedding": [vec.tolist() for vec in embeddings]
    })
    embeddings_df.to_parquet(OUTPUT_EMBEDDINGS_PARQUET, index=False)
    print(f"Saved parquet embeddings to: {OUTPUT_EMBEDDINGS_PARQUET}")

    # Sample vector for report
    sample_mid = movie_ids[0]
    sample_title = movie_titles[0]
    sample_vec_head = [round(float(x), 6) for x in embeddings[0][:6]]

    # 4. Generate Embedding Report
    report_lines = [
        "=" * 65,
        "        MOVIE EMBEDDINGS GENERATION REPORT (PHASE 5)",
        "=" * 65,
        "",
        "1. MODEL CONFIGURATION",
        f"   - Embedding Model Used:       {MODEL_NAME}",
        f"   - Embedding Dimension:        {embedding_dim}",
        f"   - Normalization:              L2 Normalized (Unit Norm for Cosine Sim)",
        f"   - Batch Size:                 {BATCH_SIZE}",
        "",
        "2. EXECUTION SUMMARY",
        f"   - Total Movies Processed:     {total_movies:,}",
        f"   - Successful Embeddings:      {successful_count:,}",
        f"   - Failed Embeddings:          {failed_count}",
        f"   - Elapsed Time:               {duration:.2f} seconds ({total_movies / duration:.1f} movies/sec)",
        f"   - Execution Result:           SUCCESS",
        "",
        "3. SAMPLE EMBEDDING (First 6 dimensions)",
        f"   - Movie ID:                   {sample_mid}",
        f"   - Title:                      {sample_title}",
        f"   - Vector Snippet (dim 0..5):  {sample_vec_head}",
        "",
        "4. OUTPUT ARTIFACTS",
        f"   - Matrix (.npy):              {OUTPUT_EMBEDDINGS_NPY}",
        f"   - Mapping Index (.json):      {OUTPUT_IDS_JSON}",
        f"   - Tabular Parquet (.parquet): {OUTPUT_EMBEDDINGS_PARQUET}",
        "=" * 65
    ]
    
    report_content = "\n".join(report_lines)
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("\n" + report_content)


if __name__ == "__main__":
    generate_embeddings()
