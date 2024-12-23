from typing import Optional, List

from geoalchemy2.elements import WKTElement
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from src.models.location import Location
from src.repositories.recomendation import LocationCategoryRepository
from .base import BaseRepository


class LocationRepository(BaseRepository[Location]):
    def __init__(self):

        super().__init__(model=Location)

    async def create_with_coordinates(
        self,
        session: AsyncSession,
        name: str,
        latitude: float,
        longitude: float,
        category: int,
        description: Optional[str] = None
    ) -> Location:
        try:
            # Create a WKTElement from the latitude and longitude
            point = WKTElement(f'POINT({longitude} {latitude})', srid=4326)
            
            # Create a new Location object with the provided data
            location = Location(
                name=name,
                latitude=latitude,
                longitude=longitude,
                point=point,
                description=description
            )
            
            # add the object to the session
            session.add(location)
            
            # Asynchronously commit the session
            await session.commit()
            
            # Refresh the object to get the updated values
            await session.refresh(location)
            location_category = LocationCategoryRepository()
       
            location_category_review = await location_category.create_relationship(session, location_id=location.id, category_id=category)
            if location_category_review:
                return location
            else:
                raise Exception("Error creando la relación entre la ubicación y la categoría")


        except SQLAlchemyError as e:
            await session.rollback()
            raise Exception(f"Error creando la ubicación: {str(e)}")

    async def get_nearby(
        self,
        session: AsyncSession,
        latitude: float,
        longitude: float,
        radius_km: float = 1.0,
        limit: int = 10
    ) -> List[Location]:
        point = WKTElement(f'POINT({longitude} {latitude})', srid=4326)

        stmt = select(Location).filter(
            func.ST_DWithin(
                Location.point,
                point,
                radius_km * 1000
            )
        ).limit(limit)

        result = await session.execute(stmt)

        locations = result.scalars().all()
        return locations