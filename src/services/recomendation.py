from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from src.services.base_service import BaseService
from src.models.review import LocationCategoryReview
from src.repositories.recomendation import RecommendationRepository, LocationCategoryRepository
from src.schemas.recomendation import ExplorationRecommendation


class RecommendationService(BaseService[LocationCategoryReview]):
    def __init__(self):
        super().__init__(RecommendationRepository)

    async def get_exploration_recommendations(
        self,
        session: AsyncSession,
        limit: int = 10
    ) -> List[ExplorationRecommendation]:
        """Get exploration recommendations based on review history"""
        try:
            return await self.repository.get_exploration_recommendations(
                db=session,
                limit=limit
            )
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting recommendations: {str(e)}"
            )

    async def record_review(
        self,
        session: AsyncSession,
        location_id: int,
        category_id: int
    ) -> None:
        """Record a new review for a location-category pair"""
        try:
            await self.repository.record_review(
                db=session,
                location_id=location_id,
                category_id=category_id
            )
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error recording review: {str(e)}"
            )

class LocationCategoryService(BaseService[LocationCategoryReview]):
    def __init__(self):
        super().__init__(LocationCategoryRepository)

    async def create_category_relationship(
        self,
        session: AsyncSession,
        location_id: int,
        category_id: int
    ) -> LocationCategoryReview:
        """Create a relationship between location and category"""
        try:
            return await self.repository.create_relationship(
                session=session,
                location_id=location_id,
                category_id=category_id
            )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating location-category relationship: {str(e)}"
            )

    async def update_location_view(
        self,
        session: AsyncSession,
        location_id: int
    ) -> Optional[LocationCategoryReview]:
        """Update the last viewed timestamp for a location"""
        try:
            return await self.repository.update_last_view(
                session=session,
                location_id=location_id
            )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating location view: {str(e)}"
            )