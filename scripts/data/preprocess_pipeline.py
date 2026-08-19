"""
Data Cleaning and Preprocessing Pipeline
=========================================
Loads TMDB movies & credits along with MovieLens ratings and the ID mapping
to create clean, normalized movie and rating datasets for downstream ML/AI systems.

Inputs:
- data/raw/tmdb_5000_movies.csv
- data/raw/tmdb_5000_credits.csv
- data/raw/ratings.dat
- data/processed/movielens_tmdb_mapping.csv

Outputs:
- data/processed/movies_clean.csv
- data/processed/ratings_clean.csv
- data/processed/preprocessing_report.txt
"""

import os
import sys
import ast
import json
from pathlib import Path
from typing import List, Any, Dict, Tuple
import pandas as pd
import numpy as np

# Windows utf-8 terminal support
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

TMDB_MOVIES_FILE = RAW_DIR / "tmdb_5000_movies.csv"
TMDB_CREDITS_FILE = RAW_DIR / "tmdb_5000_credits.csv"
RATINGS_FILE = RAW_DIR / "ratings.dat"
MAPPING_FILE = PROCESSED_DIR / "movielens_tmdb_mapping.csv"

OUT_MOVIES_CLEAN = PROCESSED_DIR / "movies_clean.csv"
OUT_RATINGS_CLEAN = PROCESSED_DIR / "ratings_clean.csv"
OUT_REPORT = PROCESSED_DIR / "preprocessing_report.txt"


def parse_json_safely(val: Any) -> List[Any]:
    """Parse JSON strings safely with fallback to ast.literal_eval."""
    if pd.isna(val) or not str(val).strip():
        return []
    val_str = str(val).strip()
    try:
        res = json.loads(val_str)
        return res if isinstance(res, list) else []
    except Exception:
        try:
            res = ast.literal_eval(val_str)
            return res if isinstance(res, list) else []
        except Exception:
            return []


def extract_names_from_json(val: Any) -> List[str]:
    """Extracts 'name' property from a list of dicts."""
    parsed = parse_json_safely(val)
    return [item.get("name", "").strip() for item in parsed if isinstance(item, dict) and item.get("name")]


def extract_director(crew_val: Any) -> str:
    """Extracts Director name from crew list."""
    parsed = parse_json_safely(crew_val)
    for member in parsed:
        if isinstance(member, dict) and member.get("job") == "Director":
            return member.get("name", "").strip()
    return ""


def extract_top_cast(cast_val: Any, top_n: int = 5) -> List[str]:
    """Extracts top N actor names from cast list."""
    parsed = parse_json_safely(cast_val)
    cast_names = []
    for item in parsed[:top_n]:
        if isinstance(item, dict) and item.get("name"):
            cast_names.append(item.get("name").strip())
    return cast_names


def clean_tmdb_movies(movies_path: Path, credits_path: Path) -> pd.DataFrame:
    """
    Cleans and merges TMDB movies and credits datasets.
    """
    print("Loading raw TMDB movies and credits...")
    movies_df = pd.read_csv(movies_path)
    credits_df = pd.read_csv(credits_path)

    # Ensure movie_id matches
    if "id" in movies_df.columns:
        movies_df = movies_df.rename(columns={"id": "movie_id"})
    if "id" in credits_df.columns and "movie_id" not in credits_df.columns:
        credits_df = credits_df.rename(columns={"id": "movie_id"})

    # Merge on movie_id
    merged = pd.merge(movies_df, credits_df[["movie_id", "cast", "crew"]], on="movie_id", how="left")

    print(f"Total merged TMDB rows: {len(merged)}")

    # Extract release year
    def extract_year(date_val):
        if pd.isna(date_val) or not isinstance(date_val, str):
            return None
        parts = date_val.strip().split("-")
        if parts and len(parts[0]) == 4 and parts[0].isdigit():
            return int(parts[0])
        return None

    # Clean runtime to integer (or nullable integer)
    def clean_runtime(r):
        if pd.isna(r) or r is None:
            return None
        try:
            val = float(r)
            return int(val) if not np.isnan(val) and val > 0 else None
        except Exception:
            return None

    # Clean overview
    def clean_overview(ov):
        if pd.isna(ov) or not str(ov).strip():
            return ""
        return str(ov).strip()

    # Build clean dataframe
    clean_records = []
    for _, row in merged.iterrows():
        mid = int(row["movie_id"])
        title = str(row["title"]).strip() if pd.notna(row["title"]) else ""
        orig_title = str(row["original_title"]).strip() if pd.notna(row["original_title"]) else ""
        overview = clean_overview(row["overview"])
        
        genres_list = extract_names_from_json(row["genres"])
        keywords_list = extract_names_from_json(row["keywords"])
        director = extract_director(row["crew"])
        cast_list = extract_top_cast(row["cast"], top_n=5)
        
        year = extract_year(row["release_date"])
        runtime = clean_runtime(row["runtime"])
        
        pop = round(float(row["popularity"]), 2) if pd.notna(row["popularity"]) else 0.0
        vote_avg = round(float(row["vote_average"]), 1) if pd.notna(row["vote_average"]) else 0.0
        vote_cnt = int(row["vote_count"]) if pd.notna(row["vote_count"]) else 0
        
        poster_path = str(row["homepage"]).strip() if pd.notna(row["homepage"]) else ""
        budget = int(row["budget"]) if pd.notna(row["budget"]) else 0
        revenue = int(row["revenue"]) if pd.notna(row["revenue"]) else 0

        clean_records.append({
            "movie_id": mid,
            "title": title,
            "original_title": orig_title,
            "overview": overview,
            "genres": json.dumps(genres_list),
            "keywords": json.dumps(keywords_list),
            "release_year": year,
            "runtime_minutes": runtime,
            "popularity_score": pop,
            "vote_average": vote_avg,
            "vote_count": vote_cnt,
            "director": director,
            "cast": json.dumps(cast_list),
            "poster_path": poster_path if poster_path else None,
            "budget": budget,
            "revenue": revenue
        })

    clean_df = pd.DataFrame(clean_records)
    return clean_df


def clean_movielens_ratings(ratings_path: Path, mapping_path: Path) -> tuple[pd.DataFrame, dict[str, any]]:
    """
    Cleans MovieLens ratings and links them with mapped TMDB movie IDs.
    Excludes ratings that have no TMDB mapping.
    """
    print("Loading MovieLens ratings.dat...")
    ratings_raw = pd.read_csv(
        ratings_path,
        sep="::",
        engine="python",
        names=["user_id", "movielens_movie_id", "rating", "timestamp"],
        encoding="latin-1"
    )
    total_ratings = len(ratings_raw)
    print(f"Total raw MovieLens ratings: {total_ratings:,}")

    print("Loading MovieLens -> TMDB mapping...")
    mapping_df = pd.read_csv(mapping_path)
    
    # Filter mapping to valid TMDB matches only
    valid_mapping = mapping_df[mapping_df["tmdb_movie_id"].notna()][["movielens_movie_id", "tmdb_movie_id"]].copy()
    valid_mapping["movielens_movie_id"] = valid_mapping["movielens_movie_id"].astype(int)
    valid_mapping["tmdb_movie_id"] = valid_mapping["tmdb_movie_id"].astype(int)

    # Merge ratings with mapping
    merged_ratings = pd.merge(ratings_raw, valid_mapping, on="movielens_movie_id", how="inner")
    
    # Organize columns
    clean_ratings_df = merged_ratings[[
        "user_id",
        "movielens_movie_id",
        "tmdb_movie_id",
        "rating",
        "timestamp"
    ]].copy()

    linked_count = len(clean_ratings_df)
    excluded_count = total_ratings - linked_count

    stats = {
        "total_raw_ratings": total_ratings,
        "linked_ratings": linked_count,
        "excluded_ratings": excluded_count,
        "linked_pct": (linked_count / total_ratings) * 100 if total_ratings > 0 else 0,
        "unique_users": clean_ratings_df["user_id"].nunique(),
        "unique_tmdb_movies_rated": clean_ratings_df["tmdb_movie_id"].nunique(),
        "rating_min": clean_ratings_df["rating"].min(),
        "rating_max": clean_ratings_df["rating"].max(),
        "duplicate_user_movie_pairs": clean_ratings_df.duplicated(subset=["user_id", "tmdb_movie_id"]).sum()
    }

    return clean_ratings_df, stats


def generate_report(movies_df: pd.DataFrame, ratings_stats: Dict[str, Any], report_path: Path):
    """Writes the comprehensive preprocessing report to text file."""
    report_lines = [
        "=" * 65,
        "       DATA PREPROCESSING & CLEANING REPORT (PHASE 3)",
        "=" * 65,
        "",
        "1. TMDB MOVIES CLEANING",
        f"   - Total TMDB Raw Movies:           {len(movies_df):,}",
        f"   - Total Cleaned Movies:            {len(movies_df):,}",
        f"   - Unique movie_id Count:           {movies_df['movie_id'].nunique():,}",
        f"   - Duplicate movie_id Count:        {movies_df['movie_id'].duplicated().sum()}",
        f"   - Movies with Missing Overview:    {(movies_df['overview'] == '').sum()}",
        f"   - Movies with Missing Year:        {movies_df['release_year'].isna().sum()}",
        f"   - Movies with Missing Runtime:     {movies_df['runtime_minutes'].isna().sum()}",
        f"   - Movies with Director Found:      {(movies_df['director'] != '').sum():,} ({((movies_df['director'] != '').sum() / len(movies_df) * 100):.1f}%)",
        "",
        "2. MOVIELENS RATINGS PREPROCESSING",
        f"   - Total Raw MovieLens Ratings:     {ratings_stats['total_raw_ratings']:,}",
        f"   - Ratings Successfully Linked:     {ratings_stats['linked_ratings']:,} ({ratings_stats['linked_pct']:.2f}%)",
        f"   - Ratings Excluded (No TMDB Map):  {ratings_stats['excluded_ratings']:,} ({(100 - ratings_stats['linked_pct']):.2f}%)",
        f"   - Unique Users Retained:           {ratings_stats['unique_users']:,}",
        f"   - Unique TMDB Movies with Ratings: {ratings_stats['unique_tmdb_movies_rated']:,}",
        f"   - Rating Score Scale:              {ratings_stats['rating_min']} to {ratings_stats['rating_max']}",
        f"   - Duplicate (User, TMDB ID) Pairs: {ratings_stats['duplicate_user_movie_pairs']}",
        "",
        "3. PROCESSED OUTPUT FILES",
        f"   - Clean Movies:  {OUT_MOVIES_CLEAN}",
        f"   - Clean Ratings: {OUT_RATINGS_CLEAN}",
        "=" * 65
    ]

    report_content = "\n".join(report_lines)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print("\n" + report_content)


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Clean TMDB movies
    clean_movies_df = clean_tmdb_movies(TMDB_MOVIES_FILE, TMDB_CREDITS_FILE)
    clean_movies_df.to_csv(OUT_MOVIES_CLEAN, index=False)
    print(f"Saved cleaned movies ({len(clean_movies_df):,} rows) to: {OUT_MOVIES_CLEAN}")

    # 2. Clean MovieLens ratings linked to TMDB
    clean_ratings_df, ratings_stats = clean_movielens_ratings(RATINGS_FILE, MAPPING_FILE)
    clean_ratings_df.to_csv(OUT_RATINGS_CLEAN, index=False)
    print(f"Saved cleaned ratings ({len(clean_ratings_df):,} rows) to: {OUT_RATINGS_CLEAN}")

    # 3. Generate summary report
    generate_report(clean_movies_df, ratings_stats, OUT_REPORT)


if __name__ == "__main__":
    main()
