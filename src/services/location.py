from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.location import LocationRepository
from src.repositories.recomendation import LocationCategoryRepository
from src.schemas.location import  LocationWithDistance
from src.models.location import Location
from sqlalchemy.exc import SQLAlchemyError
from src.services.base_service import BaseService


class LocationService(BaseService[Location]):
    def __init__(self):
        self.location_repository = LocationRepository()
        self.category_repository = LocationCategoryRepository()

    async def create_location(
        self,
        session: AsyncSession,
        name: str,
        latitude: float,
        longitude: float,
        category: int,
        description: Optional[str] = None
    ) -> Location:
        location = await self.location_repository.create_with_coordinates(
            session=session,
            name=name,
            latitude=latitude,
            longitude=longitude,
            description=description
        )
        
        category_relationship = await self.category_repository.create_relationship(
            session=session, 
            location_id=location.id, 
            category_id=category
        )
        
        if not category_relationship:
            raise Exception("Error creando la relación entre la ubicación y la categoría")
            
        return location
    
    async def get_nearby_locations(
        self,
        session: AsyncSession,
        latitude: float,
        longitude: float,
        radius_km: float,
        limit: int
    ) -> List[LocationWithDistance]:
        try:
            locations = await self.location_repository.get_nearby(
                session=session,
                latitude=latitude,
                longitude=longitude,
                radius_km=radius_km,
                limit=limit
            )

            # update last viewed
            for location in locations:
                await self.category_repository.update_last_view(
                    session=session,
                    location_id=location.id
                )
            
            return locations
            
        except SQLAlchemyError as e:
            raise Exception(f"Error retrieving nearby locations: {str(e)}")