from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
import os

from app.db.session import get_db
from app.models.user import User
from app.models.watchlist import WatchlistItem
from app.schemas.watchlist import WatchlistItemCreate, WatchlistItemResponse
from app.api.deps import get_current_user

router = APIRouter()

# Load movie lookup for details
LOOKUP_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'data', 'processed', 'movie_lookup.json')
movies_lookup = {}
try:
    with open(LOOKUP_PATH, 'r', encoding='utf-8') as f:
        movies_lookup = json.load(f)
except Exception:
    pass

@router.post("/", response_model=WatchlistItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    item_in: WatchlistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id,
        WatchlistItem.movie_id == item_in.movie_id
    ).first()
    
    if existing:
        existing.status = item_in.status
        db.commit()
        db.refresh(existing)
        item = existing
    else:
        item = WatchlistItem(
            user_id=current_user.id,
            movie_id=item_in.movie_id,
            status=item_in.status
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        
    res = WatchlistItemResponse.from_orm(item)
    res.movie_details = movies_lookup.get(str(item.movie_id))
    return res

@router.get("/", response_model=List[WatchlistItemResponse])
def get_user_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = db.query(WatchlistItem).filter(WatchlistItem.user_id == current_user.id).all()
    results = []
    for item in items:
        res = WatchlistItemResponse.from_orm(item)
        res.movie_details = movies_lookup.get(str(item.movie_id))
        results.append(res)
    return results

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id,
        WatchlistItem.movie_id == movie_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
        
    db.delete(item)
    db.commit()
    return None
