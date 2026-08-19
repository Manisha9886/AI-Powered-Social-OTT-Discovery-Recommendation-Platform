from fastapi import APIRouter
from .endpoints import health, recommendations, ai, movies

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(movies.router, prefix="/movies", tags=["movies"])