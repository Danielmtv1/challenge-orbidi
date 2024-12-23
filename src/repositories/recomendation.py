from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from src.models import Location, Category, LocationCategoryReview
from src.core.config import get_settings
from src.schemas.recomendation import ExplorationRecommendation
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)
settings = get_settings()

class RecommendationService:
    """
    Service for handling location and category recommendations
    """
    
    async def get_exploration_recommendations(
        self,
        db: AsyncSession,
        user_latitude: Optional[float] = None,
        user_longitude: Optional[float] = None,
        limit: int = 10
    ) -> List[ExplorationRecommendation]:
        """
        Get exploration recommendations based on review status and optionally location
        
        Args:
            db: Database session
            user_latitude: Optional user's latitude for nearby recommendations
            user_longitude: Optional user's longitude for nearby recommendations
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommendations ordered by priority and distance if location provided
        """
        try:
            # Subquerys for last review date
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
                .subquery()
            )

            # Query base
            query = (
                select(
                    Location,
                    Category,
                    last_reviews.c.last_reviewed
                )
                .join(Category, Category.is_active == True)
                .outerjoin(
                    last_reviews,
                    and_(
                        Location.id == last_reviews.c.location_id,
                        Category.id == last_reviews.c.category_id
                    )
                )
            )

            # filter by review expiration
            cutoff_date = datetime.utcnow() - timedelta(
                days=settings.REVIEW_EXPIRATION_DAYS
            )
            query = query.where(
                or_(
                    last_reviews.c.last_reviewed.is_(None),
                    last_reviews.c.last_reviewed < cutoff_date
                )
            )

            # Add distance column if user location provided and order by it if so 
            if user_latitude is not None and user_longitude is not None:
                distance = func.ST_Distance(
                    Location.point,
                    func.ST_SetSRID(
                        func.ST_MakePoint(user_longitude, user_latitude),
                        4326
                    )
                )
                query = query.add_columns(distance.label('distance'))
                query = query.order_by(distance)

            # Order by last review date and randomize
            query = query.order_by(
                last_reviews.c.last_reviewed.asc().nullsfirst(),
                func.random()
            )

            # Limit results to the specified amount
            query = query.limit(limit)

            # Execute query
            result = await db.execute(query)
            recommendations = result.all()

            # Build response
            return [
                ExplorationRecommendation(
                    location_id=rec.Location.id,
                    category_id=rec.Category.id,
                    location_name=rec.Location.name,
                    category_name=rec.Category.name,
                    last_reviewed_at=rec.last_reviewed,
                    distance_km=getattr(rec, 'distance', None)
                )
                for rec in recommendations
            ]

        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error getting recommendations"
            )

# todo: Add record_review method to RecommendationService
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