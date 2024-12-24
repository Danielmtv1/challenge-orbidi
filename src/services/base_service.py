from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta


ModelType = TypeVar("ModelType", bound=DeclarativeMeta)

class BaseService(Generic[ModelType]):
    """
    Base Service class that works with BaseRepository
    """
    def __init__(self, repository: Type[Any]):
        self.repository = repository()

    async def get(
        self, 
        session: AsyncSession, 
        id: int
    ) -> Optional[ModelType]:
        """Get a single record by ID"""
        return await self.repository.get(session, id)

    async def get_multi(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: dict = None,
        order_by: list = None
    ) -> List[ModelType]:
        """Get multiple records with filtering and ordering"""
        return await self.repository.get_multi(
            session,
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=order_by
        )

    async def create(
        self,
        session: AsyncSession,
        *,
        obj_in: dict
    ) -> ModelType:
        """Create a new record"""
        return await self.repository.create(session, obj_in=obj_in)

    async def update(
        self,
        session: AsyncSession,
        *,
        id: int,
        obj_in: dict
    ) -> Optional[ModelType]:
        """Update an existing record"""
        return await self.repository.update(session, id=id, obj_in=obj_in)

    async def delete(
        self,
        session: AsyncSession,
        *,
        id: int
    ) -> bool:
        """Delete a record"""
        return await self.repository.delete(session, id=id)