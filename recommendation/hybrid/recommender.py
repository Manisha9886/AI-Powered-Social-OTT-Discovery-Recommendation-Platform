import os
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional

from recommendation.popularity.recommender import PopularityRecommender
from recommendation.content_based.recommender import ContentBasedRecommender
from recommendation.collaborative.recommender import CollaborativeRecommender
from recommendation.schemas.recommendation import RecommendationItem, RecommendationEvidence, RecommendationResponse


class HybridRecommender:
    """
    Hybrid Recommendation Engine.
    Combines Popularity, Content-Based, and Collaborative Filtering candidate recommendations
    with configurable weighted scoring and produces evidence metrics for explainability.
    
    Formula:
    Final Score = (w_content * Content_Score) + (w_collab * Collaborative_Score) + (w_pop * Popularity_Score)
    """

    def __init__(
        self,
        data_dir: Optional[str] = None,
        weight_content: float = 0.45,
        weight_collab: float = 0.35,
        weight_popularity: float = 0.20
    ):
        self.data_dir = data_dir
        self.weight_content = weight_content
        self.weight_collab = weight_collab
        self.weight_popularity = weight_popularity

        self.popularity_model = PopularityRecommender(data_dir=data_dir)
        self.content_model = ContentBasedRecommender(data_dir=data_dir)
        self.collab_model = CollaborativeRecommender(data_dir=data_dir)
        self._is_initialized = False

    def initialize(self) -> bool:
        """Initialize and load data across all recommendation models."""
        if self._is_initialized:
            return True

        pop_ok = self.popularity_model.load_data()
        cnt_ok = self.content_model.load_data()
        clb_ok = self.collab_model.load_data()

        self._is_initialized = pop_ok or cnt_ok or clb_ok
        return self._is_initialized

    def recommend(
        self,
        user_id: int,
        filters: Optional[Dict[str, Any]] = None,
        user_liked_movie_ids: Optional[List[int]] = None,
        top_n: int = 10
    ) -> RecommendationResponse:
        """
        Generate hybrid recommendations and compute explainability evidence.
        """
        if not self._is_initialized:
            self.initialize()

        filters = filters or {}
        exclude_movie_ids = filters.get("exclude_movie_ids", [])
        strategy = filters.get("strategy", "hybrid")

        # 1. Fetch Candidate Pools from baseline models
        pop_candidates = self.popularity_model.recommend(
            top_n=30, filters=filters, exclude_movie_ids=exclude_movie_ids
        )

        content_candidates = []
        if user_liked_movie_ids:
            content_candidates = self.content_model.recommend_similar_movies(
                movie_ids=user_liked_movie_ids, top_n=30, exclude_movie_ids=exclude_movie_ids
            )

        collab_candidates = self.collab_model.recommend_for_user(
            user_id=user_id, top_n=30, exclude_movie_ids=exclude_movie_ids
        )

        # Handle specific single strategy requests
        if strategy == "popularity":
            selected = pop_candidates[:top_n]
            return self._build_response(user_id, selected, strategy="popularity")
        elif strategy == "content_based" and content_candidates:
            selected = content_candidates[:top_n]
            return self._build_response(user_id, selected, strategy="content_based")
        elif strategy == "collaborative" and collab_candidates:
            selected = collab_candidates[:top_n]
            return self._build_response(user_id, selected, strategy="collaborative")

        # 2. Merge and Rank Candidates for Hybrid strategy
        movie_scores: Dict[int, Dict[str, Any]] = {}

        # Collect Popularity Scores
        for item in pop_candidates:
            mid = item["movie_id"]
            if mid not in movie_scores:
                movie_scores[mid] = {"item": item, "pop": item.get("popularity_score", 0.0), "cnt": 0.0, "clb": 0.0}
            else:
                movie_scores[mid]["pop"] = item.get("popularity_score", 0.0)

        # Collect Content Scores
        for item in content_candidates:
            mid = item["movie_id"]
            if mid not in movie_scores:
                movie_scores[mid] = {"item": item, "pop": 0.0, "cnt": item.get("content_score", 0.0), "clb": 0.0}
            else:
                movie_scores[mid]["cnt"] = item.get("content_score", 0.0)

        # Collect Collaborative Scores
        for item in collab_candidates:
            mid = item["movie_id"]
            if mid not in movie_scores:
                movie_scores[mid] = {"item": item, "pop": 0.0, "cnt": 0.0, "clb": item.get("collaborative_score", 0.0)}
            else:
                movie_scores[mid]["clb"] = item.get("collaborative_score", 0.0)

        # If candidates pool is sparse, fallback to popularity candidates
        if not movie_scores and pop_candidates:
            for item in pop_candidates:
                mid = item["movie_id"]
                movie_scores[mid] = {"item": item, "pop": item.get("popularity_score", 0.5), "cnt": 0.5, "clb": 0.5}

        # 3. Compute Weighted Hybrid Score and Build Recommendation Items
        hybrid_items: List[RecommendationItem] = []

        for mid, data in movie_scores.items():
            item_raw = data["item"]
            pop_s = data["pop"]
            cnt_s = data["cnt"]
            clb_s = data["clb"]

            # Hybrid score calculation
            final_s = (
                (self.weight_content * cnt_s) +
                (self.weight_collab * clb_s) +
                (self.weight_popularity * pop_s)
            )

            # Build reason codes
            reason_codes = []
            if cnt_s > 0.4:
                reason_codes.append("GENRE_MATCH")
                reason_codes.append("SIMILAR_TO_LIKED_MOVIES")
            if clb_s > 0.4:
                reason_codes.append("HIGHLY_RATED_BY_SIMILAR_USERS")
            if pop_s > 0.6:
                reason_codes.append("POPULAR_TRENDING")

            if not reason_codes:
                reason_codes.append("TOP_RECOMMENDED")

            confidence = "high" if final_s > 0.65 else ("medium" if final_s > 0.35 else "low")

            evidence = RecommendationEvidence(
                content_similarity=round(cnt_s, 4),
                collaborative_score=round(clb_s, 4),
                popularity_score=round(pop_s, 4),
                preference_match=round(final_s, 4),
                runtime_constraint_satisfied=True
            )

            rec_item = RecommendationItem(
                movie_id=mid,
                title=item_raw.get("title", f"Movie #{mid}"),
                final_score=round(float(final_s), 4),
                content_score=round(float(cnt_s), 4),
                collaborative_score=round(float(clb_s), 4),
                popularity_score=round(float(pop_s), 4),
                genres=item_raw.get("genres", []),
                poster_path=item_raw.get("poster_path"),
                vote_average=item_raw.get("vote_average", 0.0),
                release_year=item_raw.get("release_year"),
                runtime=item_raw.get("runtime"),
                overview=item_raw.get("overview", ""),
                reason_codes=list(set(reason_codes)),
                confidence=confidence,
                evidence=evidence
            )
            hybrid_items.append(rec_item)

        # Sort by final hybrid score descending
        hybrid_items = sorted(hybrid_items, key=lambda x: x.final_score, reverse=True)[:top_n]

        return RecommendationResponse(
            user_id=user_id,
            recommendations=hybrid_items,
            strategy_used="hybrid",
            total_count=len(hybrid_items)
        )

    def _build_response(
        self, user_id: int, items: List[Dict[str, Any]], strategy: str
    ) -> RecommendationResponse:
        rec_items = []
        for item in items:
            final_s = item.get("popularity_score", item.get("content_score", item.get("collaborative_score", 0.5)))
            evidence = RecommendationEvidence(
                content_similarity=item.get("content_score", 0.0),
                collaborative_score=item.get("collaborative_score", 0.0),
                popularity_score=item.get("popularity_score", 0.0),
                preference_match=final_s,
                runtime_constraint_satisfied=True
            )
            rec_items.append(RecommendationItem(
                movie_id=item["movie_id"],
                title=item.get("title", "Unknown"),
                final_score=round(final_s, 4),
                content_score=item.get("content_score", 0.0),
                collaborative_score=item.get("collaborative_score", 0.0),
                popularity_score=item.get("popularity_score", 0.0),
                genres=item.get("genres", []),
                poster_path=item.get("poster_path"),
                vote_average=item.get("vote_average", 0.0),
                release_year=item.get("release_year"),
                runtime=item.get("runtime"),
                overview=item.get("overview", ""),
                reason_codes=item.get("reason_codes", ["TOP_RECOMMENDED"]),
                confidence="high",
                evidence=evidence
            ))
        return RecommendationResponse(
            user_id=user_id,
            recommendations=rec_items,
            strategy_used=strategy,
            total_count=len(rec_items)
        )
