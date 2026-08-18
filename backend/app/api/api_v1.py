from fastapi import APIRouter
from .endpoints import health, recommendations, ai

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
# Add other routers here as they are built: auth, users, movies, social, etc.
