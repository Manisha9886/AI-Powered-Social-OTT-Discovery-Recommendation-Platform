from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class RecommendationEvidence(BaseModel):
    content_similarity: Optional[float] = None
    collaborative_score: Optional[float] = None
    popularity_score: Optional[float] = None
    preference_match: Optional[float] = None
    
class RecommendationItem(BaseModel):
    movie_id: int
    title: str
    final_score: float
    evidence: Optional[RecommendationEvidence] = None
    reason_codes: List[str] = []
    confidence: str

class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[RecommendationItem]
