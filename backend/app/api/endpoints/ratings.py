from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
import os

from app.db.session import get_db
from app.models.user import User
from app.models.rating import UserRating
from app.schemas.rating import UserRatingCreate, UserRatingResponse
from app.api.deps import get_current_user

router = APIRouter()

LOOKUP_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'data', 'processed', 'movie_lookup.json')
movies_lookup = {}
try:
    with open(LOOKUP_PATH, 'r', encoding='utf-8') as f:
        movies_lookup = json.load(f)
except Exception:
    pass

@router.post("/", response_model=UserRatingResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_rating(
    rating_in: UserRatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(UserRating).filter(
        UserRating.user_id == current_user.id,
        UserRating.movie_id == rating_in.movie_id
    ).first()
    
    if existing:
        existing.rating = rating_in.rating
        existing.review = rating_in.review
        db.commit()
        db.refresh(existing)
        item = existing
    else:
        item = UserRating(
            user_id=current_user.id,
            movie_id=rating_in.movie_id,
            rating=rating_in.rating,
            review=rating_in.review
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        
    res = UserRatingResponse.from_orm(item)
    res.movie_details = movies_lookup.get(str(item.movie_id))
    return res

@router.get("/", response_model=List[UserRatingResponse])
def get_user_ratings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ratings = db.query(UserRating).filter(UserRating.user_id == current_user.id).all()
    results = []
    for item in ratings:
        res = UserRatingResponse.from_orm(item)
        res.movie_details = movies_lookup.get(str(item.movie_id))
        results.append(res)
    return results
