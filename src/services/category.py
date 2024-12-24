from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from src.repositories.category import CategoryRepository
from src.models.category import Category
from src.services.base_service import BaseService

class CategoryService(BaseService[Category]):
    def __init__(self):
        super().__init__(CategoryRepository)

    async def get_active_categories(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Category]:
        """Get all active categories"""
        try:
            return await self.repository.get_active_categories(
                db=session,
                skip=skip,
                limit=limit
            )
        except SQLAlchemyError as e:
            raise Exception(f"Error getting active categories: {str(e)}")

    async def get_by_name(
        self,
        session: AsyncSession,
        name: str
    ) -> Optional[Category]:
        """Get category by name"""
        try:
            return await self.repository.get_by_name(
                db=session,
                name=name
            )
        except SQLAlchemyError as e:
            raise Exception(f"Error getting category by name: {str(e)}")

    async def bulk_create_categories(
        self,
        session: AsyncSession,
        categories: List[dict]
    ) -> List[Category]:
        """Bulk create multiple categories"""
        try:
            return await self.repository.bulk_create(
                session=session,
                categories=categories
            )
        except SQLAlchemyError as e:
            raise Exception(f"Error bulk creating categories: {str(e)}")

    async def create_category(
        self,
        session: AsyncSession,
        name: str,
        description: Optional[str] = None,
        is_active: bool = True
    ) -> Category:
        """Create a single category with specific fields"""
        try:
            category_data = {
                "name": name,
                "description": description,
                "is_active": is_active
            }
            return await self.repository.create(
                session=session,
                obj_in=category_data
            )
        except SQLAlchemyError as e:
            raise Exception(f"Error creating category: {str(e)}")

    async def update_category_status(
        self,
        session: AsyncSession,
        category_id: int,
        is_active: bool
    ) -> Optional[Category]:
        """Update category active status"""
        try:
            return await self.repository.update(
                session,
                id=category_id,
                obj_in={"is_active": is_active}
            )
        except SQLAlchemyError as e:
            raise Exception(f"Error updating category status: {str(e)}")