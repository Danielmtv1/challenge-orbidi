from datetime import datetime, timedelta, timezone
from sqlalchemy import func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select  # For asynchronous select queries
from src.core.config import get_settings
from src.models.location import Location
from src.models.category import Category
from src.models.review import LocationCategoryReview
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class RecommendationService:
    @staticmethod
    async def get_exploration_recommendations(
        db: AsyncSession,
        limit: int = 10
    ) -> List[Tuple[Location, Category, datetime]]:
        try:
            # subquery for last review date
            last_reviews = (
                select(
                    LocationCategoryReview.location_id,
                    LocationCategoryReview.category_id,
                    func.max(LocationCategoryReview.last_reviewed_at).label('last_reviewed')
                )
                .group_by(
                    LocationCategoryReview.location_id,
                    LocationCategoryReview.category_id
                )
                .alias('last_reviews')  
            )
            
            # Calculate the cutoff date for reviews
            cutoff_date = datetime.now(timezone.utc) - timedelta(
                days=settings.REVIEW_EXPIRATION_DAYS
            )
            
            # Query base for recommendations
            recommendations = (
                select(
                    Location,
                    Category,
                    last_reviews.c.last_reviewed
                )
                .select_from(Location)
                .join(Category, Category.is_active == True)
                .outerjoin(
                    last_reviews,
                    and_(
                        Location.id == last_reviews.c.location_id,
                        Category.id == last_reviews.c.category_id
                    )
                )
                .filter(
                    or_(
                        last_reviews.c.last_reviewed.is_(None),
                        last_reviews.c.last_reviewed < cutoff_date
                    )
                )
                .order_by(
                    last_reviews.c.last_reviewed.asc().nullsfirst(),
                    func.random()
                )
                .limit(limit)
            )
            
            result = await db.execute(recommendations)
            return result.fetchall()
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            raise
