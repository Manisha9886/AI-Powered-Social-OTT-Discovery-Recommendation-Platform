from fastapi import APIRouter, HTTPException, Query
import json
import os
from typing import List, Optional

router = APIRouter()

# Load movie lookup data
LOOKUP_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'data', 'processed', 'movie_lookup.json')
movies_data = {}

try:
    with open(LOOKUP_PATH, 'r', encoding='utf-8') as f:
        movies_data = json.load(f)
except Exception as e:
    print(f"Failed to load movie_lookup.json: {e}")

@router.get("/")
def get_movies(page: int = Query(1, ge=1), page_size: int = Query(24, ge=1, le=100)):
    movies_list = list(movies_data.values())
    total = len(movies_list)
    
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "movies": movies_list[start:end]
    }

@router.get("/{movie_id}")
def get_movie(movie_id: str):
    if movie_id not in movies_data:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movies_data[movie_id]