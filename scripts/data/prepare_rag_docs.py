"""
RAG Knowledge Document Preparation Script
==========================================
Constructs rich, structured knowledge documents and factual lookup catalogs
for all 4,803 movies from `movies_features.csv` to power Member 3's RAG retrieval,
vector indexing, and LLM grounded explainability.

Inputs:
- data/processed/movies_features.csv

Outputs:
- data/processed/movie_knowledge_docs.json   (List of RAG documents with content + metadata)
- data/processed/movie_lookup.json           (Fast key-value lookup dict keyed by movie_id)
- data/processed/rag_docs_report.txt         (Validation and execution report)
"""

import os
import sys
import json
import ast
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

# Windows UTF-8 console output
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"

INPUT_FEATURES_FILE = PROCESSED_DIR / "movies_features.csv"
OUTPUT_RAG_DOCS_FILE = PROCESSED_DIR / "movie_knowledge_docs.json"
OUTPUT_LOOKUP_FILE = PROCESSED_DIR / "movie_lookup.json"
OUTPUT_REPORT_FILE = PROCESSED_DIR / "rag_docs_report.txt"


def parse_list_safely(val: Any) -> List[str]:
    """Parse JSON or Python string representation of lists safely."""
    if pd.isna(val) or not str(val).strip():
        return []
    val_str = str(val).strip()
    try:
        parsed = json.loads(val_str)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
    except Exception:
        pass
    try:
        parsed = ast.literal_eval(val_str)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
    except Exception:
        pass
    return []


def format_rag_content(
    title: str,
    release_year: Any,
    director: str,
    cast: List[str],
    genres: List[str],
    runtime_minutes: Any,
    vote_average: float,
    vote_count: int,
    popularity: float,
    keywords: List[str],
    overview: str
) -> str:
    """
    Formats clean, dense structured text designed for optimal semantic retrieval
    and LLM comprehension.
    """
    year_str = f" ({int(release_year)})" if pd.notna(release_year) and release_year else ""
    director_str = director if director and director.lower() != "unknown" else "Unknown Director"
    cast_str = ", ".join(cast) if cast else "Unknown Cast"
    genres_str = ", ".join(genres) if genres else "Unknown Genre"
    runtime_str = f"{int(runtime_minutes)} mins" if pd.notna(runtime_minutes) and runtime_minutes else "Unknown runtime"
    keywords_str = ", ".join(keywords) if keywords else "general themes"
    synopsis_str = overview if overview else "No detailed synopsis available."

    lines = [
        f"Movie: {title}{year_str}",
        f"Directed by: {director_str}",
        f"Starring: {cast_str}",
        f"Genres: {genres_str}",
        f"Metadata: Runtime {runtime_str} | Rating {vote_average}/10 ({vote_count:,} votes) | Popularity Score {popularity}",
        f"Keywords & Themes: {keywords_str}",
        f"Plot Synopsis: {synopsis_str}"
    ]
    return "\n".join(lines)


def build_rag_documents():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading movie features from: {INPUT_FEATURES_FILE}")
    df = pd.read_csv(INPUT_FEATURES_FILE)
    total_movies = len(df)
    print(f"Total movies to convert into RAG knowledge documents: {total_movies:,}")

    rag_documents: List[Dict[str, Any]] = []
    movie_lookup: Dict[str, Dict[str, Any]] = {}
    failed_docs = 0

    for idx, row in df.iterrows():
        try:
            mid = int(row["movie_id"])
            title = str(row["title"]).strip() if pd.notna(row["title"]) else ""
            orig_title = str(row["original_title"]).strip() if pd.notna(row["original_title"]) else ""
            overview = str(row["overview"]).strip() if pd.notna(row["overview"]) else ""
            
            genres = parse_list_safely(row["genres"])
            keywords = parse_list_safely(row["keywords"])
            cast = parse_list_safely(row["cast"])
            director = str(row["director"]).strip() if pd.notna(row["director"]) else ""
            
            year = int(row["release_year"]) if pd.notna(row["release_year"]) and row["release_year"] else None
            runtime = int(row["runtime_minutes"]) if pd.notna(row["runtime_minutes"]) and row["runtime_minutes"] else None
            vote_avg = float(row["vote_average"]) if pd.notna(row["vote_average"]) else 0.0
            vote_cnt = int(row["vote_count"]) if pd.notna(row["vote_count"]) else 0
            popularity = float(row["popularity_score"]) if pd.notna(row["popularity_score"]) else 0.0
            poster_path = str(row["poster_path"]).strip() if pd.notna(row["poster_path"]) else None
            budget = int(row["budget"]) if pd.notna(row["budget"]) else 0
            revenue = int(row["revenue"]) if pd.notna(row["revenue"]) else 0

            # Formatted chunk text
            doc_content = format_rag_content(
                title=title,
                release_year=year,
                director=director,
                cast=cast,
                genres=genres,
                runtime_minutes=runtime,
                vote_average=vote_avg,
                vote_count=vote_cnt,
                popularity=popularity,
                keywords=keywords,
                overview=overview
            )

            # Metadata packet
            metadata = {
                "movie_id": mid,
                "title": title,
                "original_title": orig_title,
                "release_year": year,
                "runtime_minutes": runtime,
                "genres": genres,
                "keywords": keywords,
                "director": director,
                "cast": cast,
                "vote_average": vote_avg,
                "vote_count": vote_cnt,
                "popularity_score": popularity,
                "poster_path": poster_path,
                "budget": budget,
                "revenue": revenue
            }

            rag_doc = {
                "doc_id": f"movie_{mid}",
                "movie_id": mid,
                "title": title,
                "content": doc_content,
                "metadata": metadata
            }

            rag_documents.append(rag_doc)
            movie_lookup[str(mid)] = metadata

        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            failed_docs += 1

    # 1. Save RAG knowledge documents (.json)
    with open(OUTPUT_RAG_DOCS_FILE, "w", encoding="utf-8") as f:
        json.dump(rag_documents, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(rag_documents):,} RAG documents to: {OUTPUT_RAG_DOCS_FILE}")

    # 2. Save Fast Lookup Catalog (.json)
    with open(OUTPUT_LOOKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(movie_lookup, f, indent=2, ensure_ascii=False)
    print(f"Saved movie factual lookup catalog to: {OUTPUT_LOOKUP_FILE}")

    # 3. Generate Report
    sample_doc = rag_documents[0] if rag_documents else {}
    sample_preview = json.dumps(sample_doc, indent=2, ensure_ascii=False)

    report_lines = [
        "=" * 65,
        "        RAG KNOWLEDGE DOCUMENT PREPARATION REPORT (PHASE 6)",
        "=" * 65,
        "",
        "1. EXECUTION SUMMARY",
        f"   - Total Movies Represented:      {total_movies:,}",
        f"   - RAG Documents Created:         {len(rag_documents):,}",
        f"   - Failed / Missing Documents:    {failed_docs}",
        f"   - Coverage Rate:                 {(len(rag_documents) / total_movies * 100):.2f}%",
        f"   - Execution Result:              SUCCESS",
        "",
        "2. DOCUMENT SCHEMA & ATTRIBUTES",
        "   - doc_id:       Unique string identifier (e.g. 'movie_19995')",
        "   - movie_id:     Integer ID mapped 1-to-1 with database and recommendations",
        "   - title:        Primary movie title",
        "   - content:      High-density structured text chunk for RAG indexing & prompt injection",
        "   - metadata:     Complete factual JSON dictionary (genres, cast, director, year, runtime, ratings)",
        "",
        "3. OUTPUT ARTIFACTS",
        f"   - RAG Knowledge Base:  {OUTPUT_RAG_DOCS_FILE}",
        f"   - Factual Lookup Dict: {OUTPUT_LOOKUP_FILE}",
        "",
        "4. SAMPLE RAG DOCUMENT PREVIEW (First Document)",
        f"{sample_preview}",
        "=" * 65
    ]

    report_content = "\n".join(report_lines)
    with open(OUTPUT_REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report_content)

    print("\n" + report_content)


if __name__ == "__main__":
    build_rag_documents()
