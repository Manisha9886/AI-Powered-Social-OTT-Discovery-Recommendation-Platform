from fastapi import APIRouter
from app.schemas.recommendations import RecommendationResponse
from recommendation.interface import recommend

router = APIRouter()

@router.get("/", response_model=RecommendationResponse)
def get_recommendations(user_id: int = 101):
    """
    Get mock recommendations for a user.
    """
    data = recommend(user_id=user_id)
    return data
