from datetime import datetime, timedelta
from typing import List

import logging

from fastapi import HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.models.category import Category
from src.models.location import Location
from src.models.review import LocationCategoryReview
from src.schemas.recomendation import ExplorationRecommendation

from .base import BaseRepository




logger = logging.getLogger(__name__)
settings = get_settings()

class RecommendationRepository(BaseRepository[LocationCategoryReview]):

    def __init__(self):

        super().__init__(model=Location)


    async def get_exploration_recommendations(
        self,
        db: AsyncSession,
        limit: int = 10
    ) -> List[ExplorationRecommendation]:
        try:
            cutoff_date = datetime.utcnow() - timedelta(
                days=settings.REVIEW_EXPIRATION_DAYS
            )
            print(f"\n cutoff_date", cutoff_date)

            query = (
                select(
                    Location.id.label('location_id'),
                    Location.name.label('location_name'),
                    Category.id.label('category_id'),
                    Category.name.label('category_name'),
                    LocationCategoryReview.last_reviewed_at
                )
                .select_from(Category)
                .join(
                    LocationCategoryReview,
                    LocationCategoryReview.category_id == Category.id,
                    isouter=True
                )
                .join(
                    Location,
                    LocationCategoryReview.location_id == Location.id
                )
                .where(
                    or_(
                        LocationCategoryReview.last_reviewed_at == None,
                        LocationCategoryReview.last_reviewed_at < cutoff_date
                    )
                )
                .order_by(
                    (LocationCategoryReview.last_reviewed_at).nullsfirst(),
                    func.random()
                )
                .limit(limit)
            )
            
            result = await db.execute(query)
            rows = result.all()
            
            return [
                ExplorationRecommendation(
                    location_id=row.location_id,
                    location_name=row.location_name,
                    category_id=row.category_id,
                    category_name=row.category_name,
                    last_reviewed_at=row.last_reviewed_at
                )
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Error getting exploration recommendations: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error getting exploration recommendations"
            )

    async def record_review(
        self,
        db: AsyncSession,
        location_id: int,
        category_id: int
    ) -> None:
        """Record a new review for a location-category pair"""
        try:
            review = LocationCategoryReview(
                location_id=location_id,
                category_id=category_id,
                last_reviewed_at=datetime.utcnow()
            )
            db.add(review)
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error(f"Error recording review: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error recording review"
            )
        
class LocationCategoryRepository(BaseRepository[LocationCategoryReview]):
    def __init__(self):
        super().__init__(LocationCategoryReview)
        
    async def create_relationship(
        self,
        session: AsyncSession,
        location_id: int,
        category_id: int
    ) -> LocationCategoryReview:
        location_category_Reviw = LocationCategoryReview(
            location_id=location_id,
            category_id=category_id,
        )
        session.add(location_category_Reviw)

        await session.commit()
        await session.refresh(location_category_Reviw)
        return location_category_Reviw

