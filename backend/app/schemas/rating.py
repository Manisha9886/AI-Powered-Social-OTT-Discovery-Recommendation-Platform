from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class UserRatingCreate(BaseModel):
    movie_id: int
    rating: float = Field(..., ge=1.0, le=5.0)
    review: Optional[str] = None

class UserRatingResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    rating: float
    review: Optional[str] = None
    created_at: datetime
    movie_details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
