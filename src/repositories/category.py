from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from src.models.category import Category
from .base import BaseRepository
import logging

logger = logging.getLogger(__name__)

class CategoryRepository(BaseRepository[Category]):
    """
    Repository for handling Category-related database operations
    """
    def __init__(self):

        super().__init__(model=Category)

    async def get_active_categories(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Category]:
        """Get all active categories"""
        try:
            query = (
                select(Category)
                .where(Category.is_active == True)
                .offset(skip)
                .limit(limit)
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching active categories: {str(e)}")
            raise

    async def get_by_name(
        self,
        db: AsyncSession,
        name: str
    ) -> Optional[Category]:
        """Get category by name"""
        try:
            query = select(Category).where(
                and_(
                    Category.name == name,
                    Category.is_active == True
                )
            )
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching category by name {name}: {str(e)}")
            raise

    async def bulk_create(
        self,
        session: AsyncSession,
        categories: List[dict]
    ) -> List[Category]:
        """Bulk create categories"""
        try:
            db_categories = [Category(**cat) for cat in categories]
            session.add_all(db_categories)
            await session.commit()
            for cat in db_categories:
                await session.refresh(cat)
            return db_categories
        except Exception as e:
            await session.rollback()
            logger.error(f"Error bulk creating categories: {str(e)}")
            raise
