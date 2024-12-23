from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.schemas.location import (
    LocationResponse,
    LocationWithDistance
)
from src.repositories.location import LocationRepository
from src.api.dependencies import verify_api_key

router = APIRouter()

@router.post(
    "/",
    response_model=LocationResponse,
    status_code=201,
    dependencies=[Depends(verify_api_key)]
)
async def create_location(
    name: str, 
    latitude: float, 
    longitude: float, 
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    # Awaiting the creation of the location
    location_repository = LocationRepository()
    location = await location_repository.create_with_coordinates(
        session=db,
        name=name,
        latitude=latitude,
        longitude=longitude,
        description=description
    )
    return location
@router.get("/nearby", response_model=List[LocationWithDistance])
async def get_nearby_locations(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=1.0, gt=0, le=10),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtain a list of nearby locations
    """
    location_repo = LocationRepository()
    location = await location_repo.get_nearby(
        session=db,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit
    )
    return location