from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RecommendationEvidence(BaseModel):
    content_similarity: float = Field(default=0.0, description="Content similarity score (0.0 to 1.0)")
    collaborative_score: float = Field(default=0.0, description="Collaborative filtering score (0.0 to 1.0)")
    popularity_score: float = Field(default=0.0, description="Popularity score (0.0 to 1.0)")
    preference_match: float = Field(default=0.0, description="User preference match score (0.0 to 1.0)")
    runtime_constraint_satisfied: bool = Field(default=True, description="Whether runtime filter was met")


class RecommendationItem(BaseModel):
    movie_id: int
    title: str
    final_score: float
    content_score: float
    collaborative_score: float
    popularity_score: float
    genres: List[str] = Field(default_factory=list)
    poster_path: Optional[str] = None
    vote_average: float = 0.0
    release_year: Optional[int] = None
    runtime: Optional[int] = None
    overview: str = ""
    reason_codes: List[str] = Field(default_factory=list)
    confidence: str = "high"
    evidence: Optional[RecommendationEvidence] = None


class RecommendationFilters(BaseModel):
    genres: Optional[List[str]] = None
    max_runtime: Optional[int] = None
    min_vote_average: Optional[float] = None
    release_year_min: Optional[int] = None
    release_year_max: Optional[int] = None
    exclude_movie_ids: Optional[List[int]] = None
    strategy: Optional[str] = "hybrid"  # "hybrid", "popularity", "content_based", "collaborative"


class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[RecommendationItem]
    strategy_used: str = "hybrid"
    total_count: int = 0
