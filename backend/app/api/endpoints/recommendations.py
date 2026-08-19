from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import json
import os

from app.db.session import get_db
from app.models.user_preference import UserPreference
from app.models.user import User
from app.api.deps import get_current_user
from recommendation.interface import recommend

router = APIRouter()

# Load movie catalog lookup for preference scoring
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'data', 'processed')
LOOKUP_PATH = os.path.join(PROCESSED_DIR, 'movie_lookup.json')

movies_data: Dict[str, Any] = {}
try:
    with open(LOOKUP_PATH, 'r', encoding='utf-8') as f:
        movies_data = json.load(f)
except Exception as e:
    print(f"Failed to load movie_lookup.json for recommendations: {e}")

def score_movie_against_preferences(
    movie: Dict[str, Any], 
    pref_genres: List[str], 
    pref_duration: List[str], 
    pref_year: List[str],
    relax_year: bool = False,
    relax_duration: bool = False
) -> float:
    # 1. Genre Score (50%)
    movie_genres = movie.get("genres", [])
    if isinstance(movie_genres, str):
        movie_genres = [g.strip() for g in movie_genres.split(",")]
        
    if not pref_genres:
        genre_score = 1.0
    else:
        matches = sum(1 for g in movie_genres if g in pref_genres)
        genre_score = min(1.0, matches / max(1, len(pref_genres)))
        
    # 2. Duration Score (20%)
    runtime = movie.get("runtime_minutes") or movie.get("runtime") or 100
    if relax_duration or not pref_duration or "any" in [d.lower() for d in pref_duration]:
        duration_score = 1.0
    else:
        duration_score = 0.0
        for dur in pref_duration:
            dur_lower = dur.lower()
            if "short" in dur_lower and runtime < 90:
                duration_score = 1.0
            elif "medium" in dur_lower and 90 <= runtime <= 120:
                duration_score = 1.0
            elif "long" in dur_lower and runtime > 120:
                duration_score = 1.0

    # 3. Release Year Score (20%)
    rel_year = movie.get("release_year") or 2010
    if relax_year or not pref_year or "any" in [y.lower() for y in pref_year]:
        year_score = 1.0
    else:
        year_score = 0.0
        for y_range in pref_year:
            y_lower = y_range.lower()
            if "new" in y_lower or "2024" in y_lower:
                if rel_year >= 2024: year_score = 1.0
            elif "recent" in y_lower or "2020" in y_lower:
                if 2020 <= rel_year <= 2023: year_score = 1.0
            elif "2010" in y_lower:
                if 2010 <= rel_year <= 2019: year_score = 1.0
            elif "2000" in y_lower:
                if 2000 <= rel_year <= 2009: year_score = 1.0
            elif "classic" in y_lower or "before 2000" in y_lower:
                if rel_year < 2000: year_score = 1.0

    # 4. Quality Score (10%)
    vote_avg = movie.get("vote_average") or movie.get("rating_score") or 7.0
    quality_score = min(1.0, max(0.0, float(vote_avg) / 10.0))

    # Weighted Composite Score
    total_score = (genre_score * 0.50) + (duration_score * 0.20) + (year_score * 0.20) + (quality_score * 0.10)
    return total_score


@router.get("/")
def get_recommendations(
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Preference-Based & Hybrid Recommendation Endpoint.
    Uses explicit user preferences if available, applying weighted scoring:
    Genre (50%) + Duration (20%) + Year (20%) + Quality (10%).
    Includes Progressive Relaxation if exact filtering produces < 5 matches.
    """
    target_user_id = user_id or 101
    
    # Check if preference exists in database for this user_id
    pref = db.query(UserPreference).filter(UserPreference.user_id == target_user_id).first()
    
    if pref and (pref.genres or pref.duration or pref.release_year):
        pref_genres = pref.genres or []
        pref_duration = pref.duration or []
        pref_year = pref.release_year or []
        
        # Phase 1: Exact preference match scoring
        scored_movies = []
        for m_id, m_data in movies_data.items():
            score = score_movie_against_preferences(m_data, pref_genres, pref_duration, pref_year)
            if score > 0.3:
                scored_movies.append((score, m_data))
                
        # Phase 2: Progressive Relaxation if fewer than 5 candidates found
        if len(scored_movies) < 5:
            scored_movies = []
            for m_id, m_data in movies_data.items():
                score = score_movie_against_preferences(m_data, pref_genres, pref_duration, pref_year, relax_year=True, relax_duration=True)
                if score > 0.2:
                    scored_movies.append((score, m_data))

        scored_movies.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored_movies[:12]

        recs = []
        for score, m_data in top_matches:
            genres_str = ", ".join(m_data.get("genres", [])) if isinstance(m_data.get("genres"), list) else ""
            recs.append({
                "movie_id": m_data.get("movie_id"),
                "title": m_data.get("title"),
                "score": round(score, 3),
                "evidence": {
                    "matched_genres": [g for g in pref_genres if g in m_data.get("genres", [])],
                    "preference_score": round(score * 100, 1)
                },
                "explanation": f"Matched based on your preferred genres ({genres_str}) and rating profile."
            })

        return {
            "user_id": target_user_id,
            "algorithm": "Explicit User Preference Matching",
            "recommendations": recs,
            "total_count": len(recs)
        }

    # Fallback to Hybrid engine
    return recommend(user_id=target_user_id)
