from fastapi import APIRouter
from .endpoints import locations, recomendations, categories

api_router = APIRouter()

api_router.include_router(
    locations.router,
    prefix="/locations",
    tags=["locations"]
)
api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["categories"]
)
api_router.include_router(
    recomendations.router,
    prefix="/recommendations",
    tags=["recommendations"]
)