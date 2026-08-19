from fastapi import APIRouter
from .endpoints import health, recommendations, ai, movies, auth, watchlist, ratings, preferences

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["preferences"])
api_router.include_router(movies.router, prefix="/movies", tags=["movies"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])
api_router.include_router(ratings.router, prefix="/ratings", tags=["ratings"])