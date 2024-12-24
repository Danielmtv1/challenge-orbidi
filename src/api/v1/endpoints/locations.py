from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.api.dependencies import verify_api_key
from src.schemas.location import LocationResponse, LocationWithDistance
from src.services.location import LocationService

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
    category: int,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    # Awaiting the creation of the location
    service = LocationService()
    return await service.create_location(
        session=db,
        name=name,
        latitude=latitude,
        longitude=longitude,
        category=category,
        description=description
    )

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
    service = LocationService()
    return await service.get_nearby_locations(
        session=db,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit
    )