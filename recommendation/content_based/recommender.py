import os
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


class ContentBasedRecommender:
    """
    Content-Based Recommender System.
    Computes movie similarity using:
    1. Pre-computed dense movie embeddings (movie_embeddings.npy) created by Data Engineering.
    2. TF-IDF vectorization on genre/overview/keywords metadata as fallback.
    """

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(base_dir, "data", "processed")

        self.data_dir = data_dir
        self.movies_df: Optional[pd.DataFrame] = None
        self.embeddings: Optional[np.ndarray] = None
        self.embedding_movie_ids: Optional[List[int]] = None
        self.similarity_matrix: Optional[np.ndarray] = None
        self.movie_id_to_index: Dict[int, int] = {}
        self._is_loaded = False

    def load_data(self) -> bool:
        """Load movies metadata and embeddings, then build similarity matrix."""
        movies_path = os.path.join(self.data_dir, "movies_clean.csv")
        embeddings_path = os.path.join(self.data_dir, "movie_embeddings.npy")
        embedding_ids_path = os.path.join(self.data_dir, "movie_embedding_ids.json")

        if not os.path.exists(movies_path):
            print(f"ContentBasedRecommender Warning: {movies_path} not found.")
            return False

        try:
            self.movies_df = pd.read_csv(movies_path)
            self.movies_df['movie_id'] = self.movies_df['movie_id'].astype(int)

            # Attempt to load dense embeddings if available
            if os.path.exists(embeddings_path) and os.path.exists(embedding_ids_path):
                self.embeddings = np.load(embeddings_path)
                with open(embedding_ids_path, 'r') as f:
                    self.embedding_movie_ids = [int(x) for x in json.load(f)]
                
                # Filter movies_df to match embedding order
                emb_id_map = {mid: i for i, mid in enumerate(self.embedding_movie_ids)}
                self.movie_id_to_index = emb_id_map
                
                # Precompute cosine similarity matrix for embeddings
                self.similarity_matrix = cosine_similarity(self.embeddings, self.embeddings)
            else:
                # Fallback: TF-IDF on genre + overview metadata
                self.movies_df['content_text'] = (
                    self.movies_df.get('genres', '').fillna('') + " " + 
                    self.movies_df.get('overview', '').fillna('')
                )
                tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
                tfidf_matrix = tfidf.fit_transform(self.movies_df['content_text'])
                self.similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
                self.movie_id_to_index = {
                    int(row['movie_id']): idx for idx, row in self.movies_df.iterrows()
                }

            self._is_loaded = True
            return True
        except Exception as e:
            print(f"ContentBasedRecommender Error loading data: {e}")
            return False

    def recommend_similar_movies(
        self,
        movie_ids: List[int],
        top_n: int = 10,
        exclude_movie_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Given a list of movie IDs liked by user, find the most content-similar movies.
        """
        if not self._is_loaded and not self.load_data():
            return []

        valid_indices = [
            self.movie_id_to_index[mid] for mid in movie_ids if mid in self.movie_id_to_index
        ]

        if not valid_indices:
            return []

        # Average similarity vector for target movies
        sim_scores = self.similarity_matrix[valid_indices].mean(axis=0)

        # Build list of (index, score)
        indexed_scores = list(enumerate(sim_scores))
        indexed_scores = sorted(indexed_scores, key=lambda x: x[1], reverse=True)

        if exclude_movie_ids is None:
            exclude_movie_ids = []
        exclude_set = set(movie_ids).union(set(exclude_movie_ids))

        results = []
        for idx, score in indexed_scores:
            if len(results) >= top_n:
                break
            
            # Map index back to movie_id
            if self.embedding_movie_ids:
                m_id = self.embedding_movie_ids[idx]
            else:
                m_id = int(self.movies_df.iloc[idx]['movie_id'])

            if m_id in exclude_set:
                continue

            movie_row = self.movies_df[self.movies_df['movie_id'] == m_id]
            if movie_row.empty:
                continue

            row = movie_row.iloc[0]
            genres_list = []
            if 'genres' in row and isinstance(row['genres'], str):
                genres_list = [g.strip() for g in row['genres'].split('|') if g.strip()]

            results.append({
                "movie_id": m_id,
                "title": str(row.get('title', 'Unknown')),
                "content_score": round(float(score), 4),
                "genres": genres_list,
                "vote_average": round(float(row.get('vote_average', 0.0)), 2),
                "overview": str(row.get('overview', '')) if pd.notna(row.get('overview')) else "",
                "release_year": int(row['release_year']) if 'release_year' in row and pd.notna(row['release_year']) else None,
                "runtime": int(row['runtime']) if 'runtime' in row and pd.notna(row['runtime']) else None,
                "poster_path": str(row['poster_path']) if 'poster_path' in row and pd.notna(row['poster_path']) else None,
                "reason_codes": ["GENRE_MATCH", "SIMILAR_TO_LIKED_MOVIES"],
            })

        return results
