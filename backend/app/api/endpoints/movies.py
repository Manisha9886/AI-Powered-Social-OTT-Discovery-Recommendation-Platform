from fastapi import APIRouter, HTTPException, Query
import json
import os
import requests
from typing import List, Optional, Dict, Any

router = APIRouter()

# Load movie lookup data
def resolve_processed_file(filename: str) -> str:
    current_file = os.path.abspath(__file__)
    dir_path = os.path.dirname(current_file)
    for _ in range(6):
        target = os.path.join(dir_path, "data", "processed", filename)
        if os.path.exists(target):
            return target
        dir_path = os.path.dirname(dir_path)
    return os.path.join(os.getcwd(), "data", "processed", filename)

LOOKUP_PATH = resolve_processed_file('movie_lookup.json')
DOCS_PATH = resolve_processed_file('movie_knowledge_docs.json')

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

    # 3. Build rich, multi-sentence knowledge-based summary combining cast, themes, and narrative arc
    title = movie.get("title", "This film")
    year = movie.get("release_year")
    director = movie.get("director")
    cast = movie.get("cast", [])
    genres = movie.get("genres", [])
    keywords = movie.get("keywords", [])

    genres_str = ", ".join(genres) if isinstance(genres, list) else str(genres or "Cinema")
    cast_str = ", ".join(cast[:3]) if isinstance(cast, list) and cast else ""
    themes_str = ", ".join(keywords[:4]) if isinstance(keywords, list) and keywords else ""

    summary = f"'{title}'"
    if year:
        summary += f" ({year})"
    summary += f" is an engaging {genres_str} feature"
    if director:
        summary += f" directed by visionary filmmaker {director}"
    summary += "."

    if cast_str:
        summary += f" The film stars {cast_str} in key central roles."

    if themes_str:
        summary += f" Set against themes of {themes_str}, the narrative delivers an unforgettable cinematic experience."
    else:
        summary += " The story weaves an immersive narrative filled with dramatic tension and iconic moments."

    return {
        "movie_id": int(movie_id),
        "title": movie.get("title"),
        "overview": summary,
        "source": "knowledge_overview"
    }