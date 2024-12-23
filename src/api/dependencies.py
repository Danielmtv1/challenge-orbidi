
from fastapi import Depends, Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

from src.core.config import get_settings

from src.repositories.location import LocationRepository, Location
from src.repositories.category import CategoryRepository, Category
from src.services.recomendation import RecommendationService

settings = get_settings()

# TODO: simulate valid API keys this should be replaced by a real API key verification
VALID_API_KEYS = {"valid-api-key-1", "valid-api-key-2"}



api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER, auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if settings.ENVIRONMENT == "development":
        return api_key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate API key"
        )
    return api_key

def get_location_repository() -> LocationRepository:
    return LocationRepository(Location)

def get_category_repository() -> CategoryRepository:
    return CategoryRepository(Category)

def get_recommendation_service() -> RecommendationService:
    return RecommendationService()
