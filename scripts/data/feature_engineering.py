"""
Movie Feature Engineering Script
=================================
Loads cleaned movie data and generates rich engineered features including:
- combined_text (for content-based similarity & NLP)
- genre_text (clean genre representation)
- people_text (director and cast names)
- year_bucket (temporal categories)
- rating_score (vote average)
- popularity_score_normalized (0-1 scaled popularity)
- vote_count_log (log1p transformed vote counts)

Inputs:
- data/processed/movies_clean.csv

Outputs:
- data/processed/movies_features.csv
- data/processed/feature_engineering_report.txt
"""

import os
import sys
import json
import ast
from pathlib import Path
from typing import List, Any
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
PROCESSED_DIR = DATA_DIR / "processed"

INPUT_MOVIES_CLEAN = PROCESSED_DIR / "movies_clean.csv"
OUTPUT_MOVIES_FEATURES = PROCESSED_DIR / "movies_features.csv"
OUTPUT_REPORT = PROCESSED_DIR / "feature_engineering_report.txt"


def parse_list_safely(val: Any) -> List[str]:
    """Parse JSON or stringified Python list safely."""
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


def build_year_bucket(year: Any) -> str:
    """Classifies release year into temporal buckets."""
    if pd.isna(year) or year is None:
        return "unknown"
    try:
        y = int(year)
        if y < 1990:
            return "before_1990"
        elif 1990 <= y <= 1999:
            return "1990_1999"
        elif 2000 <= y <= 2009:
            return "2000_2009"
        elif 2010 <= y <= 2019:
            return "2010_2019"
        else:
            return "2020_plus"
    except Exception:
        return "unknown"


def engineer_movie_features(df: pd.DataFrame) -> pd.DataFrame:
    """Applies feature transformations to the cleaned movies dataframe."""
    print("Engineering features for movies dataset...")
    
    # 1. Parse JSON list columns
    parsed_genres = df["genres"].apply(parse_list_safely)
    parsed_keywords = df["keywords"].apply(parse_list_safely)
    parsed_cast = df["cast"].apply(parse_list_safely)
    
    # 2. Build genre_text (comma-separated clean genres)
    df["genre_text"] = parsed_genres.apply(lambda g_list: ", ".join(g_list) if g_list else "Unknown")
    
    # 3. Build people_text (director + top cast)
    def make_people_text(row_idx):
        director = str(df.at[row_idx, "director"]).strip() if pd.notna(df.at[row_idx, "director"]) else ""
        cast_list = parsed_cast.iloc[row_idx]
        people = []
        if director and director.lower() != "unknown":
            people.append(director)
        people.extend(cast_list)
        return ", ".join(people) if people else "Unknown"

    df["people_text"] = [make_people_text(i) for i in range(len(df))]
    
    # 4. Build combined_text (rich structured content representation for similarity/NLP)
    def make_combined_text(row_idx):
        title = str(df.at[row_idx, "title"]).strip() if pd.notna(df.at[row_idx, "title"]) else ""
        overview = str(df.at[row_idx, "overview"]).strip() if pd.notna(df.at[row_idx, "overview"]) else ""
        genres_str = df.at[row_idx, "genre_text"]
        keywords_list = parsed_keywords.iloc[row_idx]
        keywords_str = ", ".join(keywords_list) if keywords_list else "none"
        director = str(df.at[row_idx, "director"]).strip() if pd.notna(df.at[row_idx, "director"]) else "Unknown"
        cast_list = parsed_cast.iloc[row_idx]
        cast_str = ", ".join(cast_list) if cast_list else "Unknown"
        
        parts = [
            f"Title: {title}.",
            f"Overview: {overview}" if overview else "Overview: No overview available.",
            f"Genres: {genres_str}.",
            f"Keywords: {keywords_str}.",
            f"Director: {director if director else 'Unknown'}.",
            f"Cast: {cast_str}."
        ]
        return " ".join(parts)

    df["combined_text"] = [make_combined_text(i) for i in range(len(df))]

    # 5. Build year_bucket
    df["year_bucket"] = df["release_year"].apply(build_year_bucket)

    # 6. Build rating_score
    df["rating_score"] = df["vote_average"].fillna(0.0)

    # 7. Build popularity_score_normalized (Min-Max Scaling to [0, 1])
    pop = df["popularity_score"].fillna(0.0)
    min_pop = pop.min()
    max_pop = pop.max()
    if max_pop > min_pop:
        df["popularity_score_normalized"] = ((pop - min_pop) / (max_pop - min_pop)).round(6)
    else:
        df["popularity_score_normalized"] = 0.0

    # 8. Build vote_count_log (safe log1p)
    vc = df["vote_count"].fillna(0)
    df["vote_count_log"] = np.log1p(np.maximum(0, vc)).round(4)

    return df


def generate_feature_report(df: pd.DataFrame, report_path: Path):
    """Generates a comprehensive summary report of the engineered features."""
    total_movies = len(df)
    total_cols = len(df.columns)
    dup_ids = df["movie_id"].duplicated().sum()
    
    missing_summary = df.isnull().sum()
    missing_nonzero = missing_summary[missing_summary > 0]
    
    year_bucket_counts = df["year_bucket"].value_counts().to_dict()
    
    sample_rows = df.head(3)
    sample_text = []
    for idx, r in sample_rows.iterrows():
        sample_text.append(
            f"\n--- Movie {r['movie_id']}: {r['title']} ---\n"
            f"  Year Bucket:     {r['year_bucket']}\n"
            f"  Rating Score:    {r['rating_score']}\n"
            f"  Pop (Norm):      {r['popularity_score_normalized']}\n"
            f"  Vote Count Log:  {r['vote_count_log']}\n"
            f"  Genres Text:     {r['genre_text']}\n"
            f"  People Text:     {r['people_text']}\n"
            f"  Combined Text:\n    \"{r['combined_text']}\""
        )

    report_lines = [
        "=" * 65,
        "         MOVIE FEATURE ENGINEERING REPORT (PHASE 4)",
        "=" * 65,
        "",
        "1. DATASET OVERVIEW",
        f"   - Total Movies Processed:          {total_movies:,}",
        f"   - Total Columns (Base + Features): {total_cols}",
        f"   - Duplicate movie_id Count:        {dup_ids}",
        "",
        "2. NEW ENGINEERED FEATURES",
        "   - combined_text:               Rich composite description (Title, Overview, Genres, Keywords, Director, Cast)",
        "   - genre_text:                  Clean comma-separated genres string",
        "   - people_text:                 Director and top cast members string",
        "   - year_bucket:                 Categorical era (before_1990, 1990_1999, 2000_2009, 2010_2019, 2020_plus)",
        "   - rating_score:                Direct numeric movie rating score (0.0 - 10.0)",
        "   - popularity_score_normalized: Min-Max normalized popularity score in [0.0, 1.0]",
        "   - vote_count_log:              Log-transformed vote count (log1p)",
        "",
        "3. YEAR BUCKET DISTRIBUTION",
    ]
    for b_name, b_count in year_bucket_counts.items():
        report_lines.append(f"   - {b_name:<15}: {b_count:,} ({b_count / total_movies * 100:.1f}%)")

    report_lines.extend([
        "",
        "4. MISSING VALUES SUMMARY",
    ])
    if len(missing_nonzero) == 0:
        report_lines.append("   - Zero missing values in all columns.")
    else:
        for c_name, c_cnt in missing_nonzero.items():
            report_lines.append(f"   - {c_name}: {c_cnt} missing")

    report_lines.extend([
        "",
        "5. SAMPLE ENGINEERED RECORDS",
        "".join(sample_text),
        "",
        "6. OUTPUT FILE",
        f"   - Location: {OUTPUT_MOVIES_FEATURES}",
        "=" * 65
    ])

    report_content = "\n".join(report_lines)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("\n" + report_content)


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading cleaned movies from: {INPUT_MOVIES_CLEAN}")
    movies_clean_df = pd.read_csv(INPUT_MOVIES_CLEAN)
    
    features_df = engineer_movie_features(movies_clean_df)
    
    # Save features dataframe
    features_df.to_csv(OUTPUT_MOVIES_FEATURES, index=False)
    print(f"Saved engineered movie features to: {OUTPUT_MOVIES_FEATURES}")
    
    # Generate and print report
    generate_feature_report(features_df, OUTPUT_REPORT)


if __name__ == "__main__":
    main()
