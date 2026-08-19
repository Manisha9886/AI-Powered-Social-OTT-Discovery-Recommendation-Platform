from typing import List, Dict, Any, Optional
import os
import json

from recommendation.hybrid.recommender import HybridRecommender
from recommendation.schemas.recommendation import RecommendationFilters

_hybrid_engine: Optional[HybridRecommender] = None


def get_hybrid_engine() -> HybridRecommender:
    global _hybrid_engine
    if _hybrid_engine is None:
        _hybrid_engine = HybridRecommender()
        _hybrid_engine.initialize()
    return _hybrid_engine


def recommend(user_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main entry point for generating recommendations for a user.
    Integrates Popularity, Content-Based, and Collaborative filtering models into a Hybrid response.
    
    Args:
        user_id (int): The ID of the user.
        filters (dict, optional): Search filters like max_runtime, genre, strategy, etc.
        
    Returns:
        dict: A recommendation response dictionary matching the API contract.
    """
    filters = filters or {}
    top_n = filters.get("top_n", 10)

    try:
        engine = get_hybrid_engine()
        response_model = engine.recommend(
            user_id=user_id,
            filters=filters,
            top_n=top_n
        )
        if hasattr(response_model, 'model_dump'):
            return response_model.model_dump()
        return response_model.dict()

    except Exception as e:
        print(f"Warning in recommend interface: {e}. Falling back to sample mock data.")
        # Fallback to sample mock dataset if files fail to load
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample', 'recommendations_mock.json')
            with open(data_path, 'r', encoding='utf-8') as f:
                mock_data = json.load(f)
                mock_data["user_id"] = user_id
                return mock_data
        except Exception:
            return {
                "user_id": user_id,
                "recommendations": [],
                "strategy_used": "fallback",
                "total_count": 0
            }
