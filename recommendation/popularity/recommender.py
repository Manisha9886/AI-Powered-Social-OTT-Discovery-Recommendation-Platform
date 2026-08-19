import os
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional


class PopularityRecommender:
    """
    Popularity-based Recommender system using IMDB/TMDB Bayesian Weighted Rating formula:
    WR = (v / (v + m)) * R + (m / (v + m)) * C
    where:
        v = number of votes for the movie
        m = minimum votes required to be listed in top charts (quantile threshold)
        R = average rating of the movie
        C = mean vote across the whole dataset
    """

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            # Default path relative to project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(base_dir, "data", "processed")

        self.data_dir = data_dir
        self.movies_df: Optional[pd.DataFrame] = None
        self._is_loaded = False

    def load_data(self) -> bool:
        """Load processed movies CSV and compute weighted rating scores."""
        movies_path = os.path.join(self.data_dir, "movies_clean.csv")
        features_path = os.path.join(self.data_dir, "movies_features.csv")

        target_path = movies_path if os.path.exists(movies_path) else features_path
        if not os.path.exists(target_path):
            print(f"PopularityRecommender Warning: Data file {target_path} not found.")
            return False

        try:
            df = pd.read_csv(target_path)
            
            # Standardize column names
            if 'vote_average' not in df.columns and 'rating' in df.columns:
                df['vote_average'] = df['rating']
            if 'vote_count' not in df.columns and 'num_ratings' in df.columns:
                df['vote_count'] = df['num_ratings']
                
            df['vote_average'] = df.get('vote_average', pd.Series(0.0)).fillna(0.0)
            df['vote_count'] = df.get('vote_count', pd.Series(0)).fillna(0)

            # Compute Bayesian Weighted Rating
            C = df['vote_average'].mean()
            m = df['vote_count'].quantile(0.70) if len(df) > 10 else 1.0
            
            def weighted_rating(x):
                v = x['vote_count']
                R = x['vote_average']
                return (v / (v + m) * R) + (m / (v + m) * C)

            df['popularity_score'] = df.apply(weighted_rating, axis=1)
            
            # Normalize popularity score between 0.0 and 1.0
            min_score = df['popularity_score'].min()
            max_score = df['popularity_score'].max()
            if max_score > min_score:
                df['popularity_score_norm'] = (df['popularity_score'] - min_score) / (max_score - min_score)
            else:
                df['popularity_score_norm'] = 0.5

            self.movies_df = df.sort_values(by='popularity_score_norm', ascending=False)
            self._is_loaded = True
            return True
        except Exception as e:
            print(f"PopularityRecommender Error loading data: {e}")
            return False

    def recommend(
        self,
        top_n: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        exclude_movie_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate popularity recommendations with optional filtering.
        """
        if not self._is_loaded and not self.load_data():
            return []

        df = self.movies_df.copy()

        if exclude_movie_ids:
            df = df[~df['movie_id'].isin(exclude_movie_ids)]

        if filters:
            # Filter by genre if specified
            if filters.get('genres'):
                target_genres = [g.lower() for g in filters['genres']]
                def genre_match(genres_val):
                    if isinstance(genres_val, str):
                        return any(tg in genres_val.lower() for tg in target_genres)
                    return True
                if 'genres' in df.columns:
                    df = df[df['genres'].apply(genre_match)]

            # Filter by max runtime
            if filters.get('max_runtime') and 'runtime' in df.columns:
                df = df[df['runtime'] <= filters['max_runtime']]

            # Filter by min rating
            if filters.get('min_vote_average') and 'vote_average' in df.columns:
                df = df[df['vote_average'] >= filters['min_vote_average']]

        top_df = df.head(top_n)

        results = []
        for _, row in top_df.iterrows():
            genres_list = []
            if 'genres' in row and isinstance(row['genres'], str):
                genres_list = [g.strip() for g in row['genres'].split('|') if g.strip()]

            results.append({
                "movie_id": int(row['movie_id']),
                "title": str(row.get('title', 'Unknown Title')),
                "popularity_score": round(float(row.get('popularity_score_norm', 0.5)), 4),
                "vote_average": round(float(row.get('vote_average', 0.0)), 2),
                "vote_count": int(row.get('vote_count', 0)),
                "genres": genres_list,
                "overview": str(row.get('overview', '')) if pd.notna(row.get('overview')) else "",
                "release_year": int(row['release_year']) if 'release_year' in row and pd.notna(row['release_year']) else None,
                "runtime": int(row['runtime']) if 'runtime' in row and pd.notna(row['runtime']) else None,
                "poster_path": str(row['poster_path']) if 'poster_path' in row and pd.notna(row['poster_path']) else None,
                "reason_codes": ["POPULAR_TRENDING", "TOP_RATED"],
            })

        return results
