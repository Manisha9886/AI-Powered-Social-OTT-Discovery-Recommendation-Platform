"""
MovieLens to TMDB ID Mapping Script
====================================
Maps MovieLens 1M movie IDs to TMDB 5000 movie IDs based on normalized titles
and release years without downloading any external files or calling external APIs.

Inputs:
- data/raw/tmdb_5000_movies.csv
- data/raw/movies.dat

Output:
- data/processed/movielens_tmdb_mapping.csv
"""

import os
import sys
import re
import unicodedata
from pathlib import Path
from typing import Tuple, Optional, Dict, List, Any
import pandas as pd

# Handle Windows terminal utf-8 output
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

TMDB_FILE = RAW_DIR / "tmdb_5000_movies.csv"
MOVIELENS_FILE = RAW_DIR / "movies.dat"
OUTPUT_MAPPING_FILE = PROCESSED_DIR / "movielens_tmdb_mapping.csv"


def normalize_title(title: str) -> str:
    """
    Normalize movie title:
    - Lowercase
    - Unicode NFKD to ASCII
    - Replace '&' with 'and'
    - Strip punctuation and extra whitespaces
    """
    if not isinstance(title, str) or not title:
        return ""
    # Unicode decomposition
    title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("utf-8")
    title = title.lower()
    title = title.replace("&", " and ")
    title = re.sub(r"[^a-z0-9\s]", " ", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def parse_movielens_title(raw_title: str) -> Tuple[str, Optional[int], List[str]]:
    """
    Parses MovieLens raw title strings:
    - Extracts 4-digit release year from trailing (YYYY)
    - Re-orders trailing articles (e.g. 'Matrix, The' -> 'The Matrix')
    - Handles alternate titles in parentheses (e.g. 'Postman, The (Il Postino) (1994)')
    """
    raw_title = raw_title.strip()
    
    # 1. Extract trailing year (YYYY)
    year = None
    year_match = re.search(r"\((\d{4})\)\s*$", raw_title)
    if year_match:
        year = int(year_match.group(1))
        title_no_year = re.sub(r"\s*\(\d{4}\)\s*$", "", raw_title).strip()
    else:
        title_no_year = raw_title

    # 2. Extract potential alternate/foreign titles in parentheses
    alt_titles = []
    alt_match = re.search(r"\(([^)]+)\)$", title_no_year)
    if alt_match and not alt_match.group(1).lower().startswith("a.k.a"):
        alt_titles.append(alt_match.group(1).strip())
        main_title = re.sub(r"\s*\([^)]+\)$", "", title_no_year).strip()
    else:
        main_title = title_no_year

    def fix_trailing_articles(t: str) -> str:
        articles = ["The", "A", "An", "Le", "La", "Les", "Der", "Die", "Das", "El", "Il", "L'"]
        for art in articles:
            m = re.match(rf"^(.*?),\s+({art})$", t, re.IGNORECASE)
            if m:
                return f"{m.group(2)} {m.group(1)}".strip()
        return t

    cleaned_main = fix_trailing_articles(main_title)
    cleaned_alts = [fix_trailing_articles(a) for a in alt_titles]
    
    return cleaned_main, year, cleaned_alts


def load_tmdb_movies(filepath: Path) -> pd.DataFrame:
    """Loads and prepares TMDB movies."""
    df = pd.read_csv(filepath)
    
    # Extract release year from release_date (YYYY-MM-DD)
    def extract_year(date_val):
        if pd.isna(date_val) or not isinstance(date_val, str):
            return None
        parts = date_val.strip().split("-")
        if parts and len(parts[0]) == 4 and parts[0].isdigit():
            return int(parts[0])
        return None

    df["release_year"] = df["release_date"].apply(extract_year)
    df["norm_title"] = df["title"].apply(normalize_title)
    df["norm_orig_title"] = df["original_title"].apply(normalize_title)
    
    return df


def load_movielens_movies(filepath: Path) -> pd.DataFrame:
    """Loads and parses MovieLens movies.dat."""
    rows = []
    with open(filepath, "r", encoding="latin-1") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("::")
            if len(parts) >= 2:
                movie_id = int(parts[0])
                raw_title = parts[1]
                genres = parts[2] if len(parts) > 2 else ""
                clean_title, year, alt_titles = parse_movielens_title(raw_title)
                rows.append({
                    "movielens_movie_id": movie_id,
                    "movielens_raw_title": raw_title,
                    "clean_title": clean_title,
                    "alt_titles": alt_titles,
                    "release_year": year,
                    "genres": genres,
                    "norm_title": normalize_title(clean_title)
                })
    return pd.DataFrame(rows)


def match_datasets(ml_df: pd.DataFrame, tmdb_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Matches MovieLens movies to TMDB movies with multiple deterministic priority levels.
    """
    matched_records = []
    ambiguous_records = []
    
    # Create lookup indices for TMDB
    # 1. (norm_title, release_year) -> list of tmdb rows
    title_year_index: Dict[Tuple[str, int], List[Dict]] = {}
    # 2. norm_title -> list of tmdb rows
    title_only_index: Dict[str, List[Dict]] = {}
    # 3. (norm_orig_title, release_year) -> list of tmdb rows
    orig_title_year_index: Dict[Tuple[str, int], List[Dict]] = {}

    for _, row in tmdb_df.iterrows():
        t_id = int(row["id"])
        t_title = row["title"]
        t_year = row["release_year"]
        norm_t = row["norm_title"]
        norm_orig = row["norm_orig_title"]
        
        entry = {
            "tmdb_movie_id": t_id,
            "tmdb_title": t_title,
            "release_year": t_year,
            "norm_title": norm_t,
            "norm_orig_title": norm_orig
        }
        
        if norm_t:
            if t_year is not None and pd.notna(t_year):
                title_year_index.setdefault((norm_t, int(t_year)), []).append(entry)
            title_only_index.setdefault(norm_t, []).append(entry)
            
        if norm_orig and t_year is not None and pd.notna(t_year):
            orig_title_year_index.setdefault((norm_orig, int(t_year)), []).append(entry)

    # Match each MovieLens movie
    for _, ml_row in ml_df.iterrows():
        ml_id = ml_row["movielens_movie_id"]
        ml_title = ml_row["movielens_raw_title"]
        ml_norm = ml_row["norm_title"]
        ml_year = ml_row["release_year"]
        ml_alts = ml_row["alt_titles"]
        
        match = None
        method = None
        confidence = 0.0
        
        # Priority 1: Exact title + Exact year
        if ml_norm and ml_year and (ml_norm, ml_year) in title_year_index:
            candidates = title_year_index[(ml_norm, ml_year)]
            if len(candidates) == 1:
                match = candidates[0]
                method = "exact_title_and_year"
                confidence = 1.0
            else:
                ambiguous_records.append({"ml_id": ml_id, "ml_title": ml_title, "reason": "multiple TMDB exact title+year"})

        # Priority 2: Exact title + Year difference of +/- 1 (international release lag)
        if not match and ml_norm and ml_year:
            year_diff_candidates = []
            for y_offset in [-1, 1]:
                if (ml_norm, ml_year + y_offset) in title_year_index:
                    year_diff_candidates.extend(title_year_index[(ml_norm, ml_year + y_offset)])
            if len(year_diff_candidates) == 1:
                match = year_diff_candidates[0]
                method = "exact_title_year_diff_1"
                confidence = 0.95
            elif len(year_diff_candidates) > 1:
                ambiguous_records.append({"ml_id": ml_id, "ml_title": ml_title, "reason": "multiple TMDB title with +/-1 year"})

        # Priority 3: Alternate title + Exact year
        if not match and ml_year and ml_alts:
            for alt in ml_alts:
                norm_alt = normalize_title(alt)
                if (norm_alt, ml_year) in title_year_index:
                    candidates = title_year_index[(norm_alt, ml_year)]
                    if len(candidates) == 1:
                        match = candidates[0]
                        method = "alt_title_and_year"
                        confidence = 0.90
                        break
                if (norm_alt, ml_year) in orig_title_year_index:
                    candidates = orig_title_year_index[(norm_alt, ml_year)]
                    if len(candidates) == 1:
                        match = candidates[0]
                        method = "alt_orig_title_and_year"
                        confidence = 0.90
                        break

        # Priority 4: Original title in TMDB + Exact year
        if not match and ml_norm and ml_year and (ml_norm, ml_year) in orig_title_year_index:
            candidates = orig_title_year_index[(ml_norm, ml_year)]
            if len(candidates) == 1:
                match = candidates[0]
                method = "original_title_and_year"
                confidence = 0.90

        # Priority 5: Unique exact title in both databases (only if release year matches or is missing)
        if not match and ml_norm in title_only_index:
            candidates = title_only_index[ml_norm]
            if len(candidates) == 1:
                tmdb_cand = candidates[0]
                # Only match if year is missing or matches exactly
                if ml_year is None or tmdb_cand["release_year"] is None or ml_year == tmdb_cand["release_year"]:
                    match = tmdb_cand
                    method = "unique_exact_title"
                    confidence = 0.85

        if match:
            matched_records.append({
                "movielens_movie_id": ml_id,
                "movielens_title": ml_title,
                "tmdb_movie_id": match["tmdb_movie_id"],
                "tmdb_title": match["tmdb_title"],
                "release_year": match["release_year"] if match["release_year"] is not None else ml_year,
                "match_method": method,
                "match_confidence": confidence
            })
        else:
            matched_records.append({
                "movielens_movie_id": ml_id,
                "movielens_title": ml_title,
                "tmdb_movie_id": None,
                "tmdb_title": None,
                "release_year": ml_year,
                "match_method": "unmatched",
                "match_confidence": 0.0
            })

    mapping_df = pd.DataFrame(matched_records)
    
    stats = {
        "total_movielens": len(ml_df),
        "total_tmdb": len(tmdb_df),
        "matched_count": mapping_df["tmdb_movie_id"].notna().sum(),
        "unmatched_count": mapping_df["tmdb_movie_id"].isna().sum(),
        "ambiguous_count": len(ambiguous_records),
        "ambiguous_details": ambiguous_records
    }
    
    return mapping_df, stats


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Loading TMDB movies...")
    tmdb_df = load_tmdb_movies(TMDB_FILE)
    print(f"Loaded {len(tmdb_df)} TMDB movies.")
    
    print("Loading MovieLens movies...")
    ml_df = load_movielens_movies(MOVIELENS_FILE)
    print(f"Loaded {len(ml_df)} MovieLens movies.")
    
    print("Matching MovieLens to TMDB...")
    mapping_df, stats = match_datasets(ml_df, tmdb_df)
    
    # Save mapping file
    mapping_df.to_csv(OUTPUT_MAPPING_FILE, index=False)
    print(f"\nSaved mapping file to: {OUTPUT_MAPPING_FILE}")
    
    # Match statistics
    matched_df = mapping_df[mapping_df["tmdb_movie_id"].notna()]
    unmatched_df = mapping_df[mapping_df["tmdb_movie_id"].isna()]
    match_pct = (stats["matched_count"] / stats["total_movielens"]) * 100
    
    # Check for duplicate mappings
    duplicate_tmdb_ids = matched_df[matched_df.duplicated(subset=["tmdb_movie_id"], keep=False)]
    
    print("=" * 60)
    print("           MOVIELENS -> TMDB MAPPING REPORT")
    print("=" * 60)
    print(f"Total MovieLens Movies:      {stats['total_movielens']:,}")
    print(f"Total TMDB 5000 Movies:      {stats['total_tmdb']:,}")
    print(f"Successfully Matched Movies: {stats['matched_count']:,}")
    print(f"Unmatched Movies:            {stats['unmatched_count']:,}")
    print(f"Match Percentage:            {match_pct:.2f}%")
    print(f"Duplicate TMDB Mappings:     {len(duplicate_tmdb_ids):,}")
    print(f"Ambiguous Match Flags:       {stats['ambiguous_count']:,}")
    print("=" * 60)
    
    print("\n--- Match Method Breakdown ---")
    print(matched_df["match_method"].value_counts())
    
    print("\n--- Sample Successful Matches (Top 10) ---")
    sample_matches = matched_df[["movielens_movie_id", "movielens_title", "tmdb_movie_id", "tmdb_title", "match_method", "match_confidence"]].head(10)
    print(sample_matches.to_string(index=False))
    
    print("\n--- Sample Unmatched Movies (Top 5) ---")
    print(unmatched_df[["movielens_movie_id", "movielens_title", "release_year"]].head(5).to_string(index=False))


if __name__ == "__main__":
    main()
