from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class WatchlistItemCreate(BaseModel):
    movie_id: int
    status: Optional[str] = "plan_to_watch"

class WatchlistItemResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    status: str
    added_at: datetime
    movie_details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
