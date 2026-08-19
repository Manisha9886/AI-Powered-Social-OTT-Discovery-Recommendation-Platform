import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any


def prepare_user_item_matrix(ratings_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[int, int], Dict[int, int]]:
    """
    Transform ratings dataframe into user-item matrix with ID index mappings.
    """
    user_col = 'user_id' if 'user_id' in ratings_df.columns else 'userId'
    movie_col = 'tmdb_movie_id' if 'tmdb_movie_id' in ratings_df.columns else ('movie_id' if 'movie_id' in ratings_df.columns else 'movieId')
    
    unique_users = ratings_df[user_col].unique()
    unique_movies = ratings_df[movie_col].unique()

    user_map = {uid: idx for idx, uid in enumerate(unique_users)}
    movie_map = {mid: idx for idx, mid in enumerate(unique_movies)}

    matrix_df = ratings_df.pivot(index=user_col, columns=movie_col, values='rating').fillna(0)
    return matrix_df, user_map, movie_map


def normalize_scores(scores: np.ndarray) -> np.ndarray:
    """Normalize score values between 0.0 and 1.0."""
    min_val, max_val = scores.min(), scores.max()
    if max_val > min_val:
        return (scores - min_val) / (max_val - min_val)
    return np.full_like(scores, 0.5)
