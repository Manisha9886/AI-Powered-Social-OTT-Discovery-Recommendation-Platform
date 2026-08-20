from fastapi import APIRouter, HTTPException, Query
import json
import os
import requests
from typing import List, Optional, Dict, Any

router = APIRouter()

# Load movie lookup data
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'data', 'processed')
LOOKUP_PATH = os.path.join(PROCESSED_DIR, 'movie_lookup.json')
DOCS_PATH = os.path.join(PROCESSED_DIR, 'movie_knowledge_docs.json')

movies_data: Dict[str, Any] = {}
knowledge_cache: Dict[str, str] = {}

try:
    with open(LOOKUP_PATH, 'r', encoding='utf-8') as f:
        movies_data = json.load(f)
except Exception as e:
    print(f"Failed to load movie_lookup.json: {e}")

try:
    with open(DOCS_PATH, 'r', encoding='utf-8') as f:
        docs = json.load(f)
        for doc in docs:
            movie_id = str(doc.get("movie_id"))
            content = doc.get("content", "")
            if "Plot Synopsis:" in content:
                synopsis = content.split("Plot Synopsis:")[-1].strip()
                knowledge_cache[movie_id] = synopsis
            elif content:
                knowledge_cache[movie_id] = content
except Exception as e:
    print(f"Failed to load movie_knowledge_docs.json: {e}")

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

@router.get("/{movie_id}/overview")
def get_movie_overview(movie_id: str):
    """
    Knowledge-Based Overview Service for Movies.
    1. Checks cached knowledge docs (movie_knowledge_docs.json).
    2. Checks TMDB API if TMDB_API_KEY is set in environment.
    3. Falls back gracefully to metadata summary or "Overview is currently unavailable".
    """
    str_id = str(movie_id)
    movie = movies_data.get(str_id)
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # 1. Check overview in movie dictionary
    plot_overview = movie.get("overview") or movie.get("content")
    if plot_overview and len(str(plot_overview).strip()) > 10:
        return {
            "movie_id": int(movie_id),
            "title": movie.get("title"),
            "overview": plot_overview,
            "source": "movie_facts"
        }

    # 2. Check local knowledge cache
    if str_id in knowledge_cache and knowledge_cache[str_id]:
        return {
            "movie_id": int(movie_id),
            "title": movie.get("title"),
            "overview": knowledge_cache[str_id],
            "source": "knowledge_base"
        }

    # 2. Check external TMDB API if configured
    tmdb_key = os.getenv("TMDB_API_KEY")
    if tmdb_key:
        try:
            url = f"https://api.themoviedb.org/3/movie/{str_id}?api_key={tmdb_key}&language=en-US"
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                overview = data.get("overview")
                if overview:
                    knowledge_cache[str_id] = overview
                    return {
                        "movie_id": int(movie_id),
                        "title": movie.get("title"),
                        "overview": overview,
                        "source": "external_api"
                    }
        except Exception:
            pass

    # 3. Metadata summary fallback
    genres = ", ".join(movie.get("genres", [])) if isinstance(movie.get("genres"), list) else ""
    director = movie.get("director", "")
    release_year = movie.get("release_year", "")
    
    if genres or director:
        summary = f"'{movie.get('title')}' is a {release_year} film"
        if genres:
            summary += f" spanning {genres}"
        if director:
            summary += f", directed by {director}"
        summary += "."
        return {
            "movie_id": int(movie_id),
            "title": movie.get("title"),
            "overview": summary,
            "source": "metadata_summary"
        }

    # 4. Graceful fallback
    return {
        "movie_id": int(movie_id),
        "title": movie.get("title"),
        "overview": "Overview is currently unavailable for this movie.",
        "source": "fallback"
    }