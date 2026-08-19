from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class UserPreferenceCreate(BaseModel):
    genres: List[str] = Field(default_factory=list)
    duration: List[str] = Field(default_factory=list)
    release_year: List[str] = Field(default_factory=list)

class UserPreferenceResponse(BaseModel):
    id: int
    user_id: int
    genres: List[str]
    duration: List[str]
    release_year: List[str]
    onboarding_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
