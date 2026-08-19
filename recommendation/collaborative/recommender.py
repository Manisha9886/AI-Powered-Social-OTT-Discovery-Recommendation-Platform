import os
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD


class CollaborativeRecommender:
    """
    Collaborative Filtering Recommender System.
    Uses Matrix Factorization (TruncatedSVD) on user-item interaction matrix (ratings_clean.csv)
    to predict user preferences based on collaborative patterns of similar users.
    """

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(base_dir, "data", "processed")

        self.data_dir = data_dir
        self.ratings_df: Optional[pd.DataFrame] = None
        self.movies_df: Optional[pd.DataFrame] = None
        self.user_item_matrix: Optional[csr_matrix] = None
        self.svd_model: Optional[TruncatedSVD] = None
        self.user_map: Dict[int, int] = {}
        self.item_map: Dict[int, int] = {}
        self.reverse_item_map: Dict[int, int] = {}
        self._is_loaded = False

    def load_data(self) -> bool:
        """Load ratings_clean.csv and train TruncatedSVD matrix factorization model."""
        ratings_path = os.path.join(self.data_dir, "ratings_clean.csv")
        movies_path = os.path.join(self.data_dir, "movies_clean.csv")

        if not os.path.exists(ratings_path) or not os.path.exists(movies_path):
            print(f"CollaborativeRecommender Warning: {ratings_path} or {movies_path} missing.")
            return False

        try:
            # Sample ratings if file is large for fast performance
            self.ratings_df = pd.read_csv(ratings_path)
            self.movies_df = pd.read_csv(movies_path)

            if 'tmdb_movie_id' in self.ratings_df.columns and 'movie_id' not in self.ratings_df.columns:
                self.ratings_df['movie_id'] = self.ratings_df['tmdb_movie_id']

            self.ratings_df['user_id'] = self.ratings_df['user_id'].astype(int)
            self.ratings_df['movie_id'] = self.ratings_df['movie_id'].astype(int)
            self.movies_df['movie_id'] = self.movies_df['movie_id'].astype(int)

            unique_users = self.ratings_df['user_id'].unique()
            unique_items = self.ratings_df['movie_id'].unique()

            self.user_map = {uid: idx for idx, uid in enumerate(unique_users)}
            self.item_map = {mid: idx for idx, mid in enumerate(unique_items)}
            self.reverse_item_map = {idx: mid for mid, idx in self.item_map.items()}

            row_indices = [self.user_map[u] for u in self.ratings_df['user_id']]
            col_indices = [self.item_map[m] for m in self.ratings_df['movie_id']]
            ratings = self.ratings_df['rating'].values

            num_users = len(unique_users)
            num_items = len(unique_items)
            self.user_item_matrix = csr_matrix((ratings, (row_indices, col_indices)), shape=(num_users, num_items))

            # Train SVD Matrix Factorization
            n_components = min(20, min(num_users, num_items) - 1)
            if n_components > 2:
                self.svd_model = TruncatedSVD(n_components=n_components, random_state=42)
                self.user_features = self.svd_model.fit_transform(self.user_item_matrix)
                self.item_features = self.svd_model.components_.T
            else:
                self.svd_model = None

            self._is_loaded = True
            return True
        except Exception as e:
            print(f"CollaborativeRecommender Error loading data: {e}")
            return False

    def recommend_for_user(
        self,
        user_id: int,
        top_n: int = 10,
        exclude_movie_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate collaborative recommendations for a specific user ID.
        """
        if not self._is_loaded and not self.load_data():
            return []

        if user_id not in self.user_map or self.svd_model is None:
            # Fallback for new/unknown user
            return []

        user_idx = self.user_map[user_id]
        
        # Predict rating scores across all items for this user: user_vector * item_features^T
        user_vec = self.user_features[user_idx]
        predicted_scores = np.dot(user_vec, self.item_features.T)

        # Normalize predicted scores between 0 and 1
        min_s, max_s = predicted_scores.min(), predicted_scores.max()
        if max_s > min_s:
            norm_scores = (predicted_scores - min_s) / (max_s - min_s)
        else:
            norm_scores = np.full_like(predicted_scores, 0.5)

        # Filter out already rated movies by user
        user_rated_items = set(
            self.ratings_df[self.ratings_df['user_id'] == user_id]['movie_id'].unique()
        )
        if exclude_movie_ids:
            user_rated_items.update(exclude_movie_ids)

        indexed_scores = sorted(enumerate(norm_scores), key=lambda x: x[1], reverse=True)

        results = []
        for item_idx, score in indexed_scores:
            if len(results) >= top_n:
                break
            
            movie_id = self.reverse_item_map[item_idx]
            if movie_id in user_rated_items:
                continue

            movie_row = self.movies_df[self.movies_df['movie_id'] == movie_id]
            if movie_row.empty:
                continue

            row = movie_row.iloc[0]
            genres_list = []
            if 'genres' in row and isinstance(row['genres'], str):
                genres_list = [g.strip() for g in row['genres'].split('|') if g.strip()]

            results.append({
                "movie_id": movie_id,
                "title": str(row.get('title', 'Unknown')),
                "collaborative_score": round(float(score), 4),
                "genres": genres_list,
                "vote_average": round(float(row.get('vote_average', 0.0)), 2),
                "overview": str(row.get('overview', '')) if pd.notna(row.get('overview')) else "",
                "release_year": int(row['release_year']) if 'release_year' in row and pd.notna(row['release_year']) else None,
                "runtime": int(row['runtime']) if 'runtime' in row and pd.notna(row['runtime']) else None,
                "poster_path": str(row['poster_path']) if 'poster_path' in row and pd.notna(row['poster_path']) else None,
                "reason_codes": ["HIGHLY_RATED_BY_SIMILAR_USERS", "COLLABORATIVE_MATCH"],
            })

        return results
