import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import  declarative_base
from src.services.base_service import BaseService


# create a declarative base for testing
Base = declarative_base()


class FakeModel(Base):
    __tablename__ = 'fake_model'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class FakeRepository:
    async def get(self, session: AsyncSession, id: int):
        pass
    
    async def get_multi(self, session: AsyncSession, skip: int = 0, limit: int = 100, 
                       filters: dict = None, order_by: list = None):
        pass
    
    async def create(self, session: AsyncSession, obj_in: dict):
        pass
    
    async def update(self, session: AsyncSession, id: int, obj_in: dict):
        pass
    
    async def delete(self, session: AsyncSession, id: int):
        pass

@pytest.fixture
def mock_repository():
    repository = FakeRepository()
    for method in ['get', 'get_multi', 'create', 'update', 'delete']:
        setattr(repository, method, AsyncMock())
    return repository

@pytest.fixture
def base_service(mock_repository):
    class TestBaseService(BaseService[FakeModel]):
        pass
    
    service = TestBaseService(FakeRepository)
    service.repository = mock_repository
    return service

@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)

@pytest.mark.asyncio
async def test_get(base_service, mock_session):
    fake_model = FakeModel()
    base_service.repository.get.return_value = fake_model
    
    result = await base_service.get(mock_session, id=1)
    
    assert result == fake_model
    base_service.repository.get.assert_called_once_with(mock_session, 1)

@pytest.mark.asyncio
async def test_get_multi(base_service, mock_session):
    fake_models = [FakeModel(), FakeModel()]
    base_service.repository.get_multi.return_value = fake_models
    filters = {"status": "active"}
    order_by = ["created_at"]
    
    results = await base_service.get_multi(
        mock_session, 
        skip=10, 
        limit=20, 
        filters=filters, 
        order_by=order_by
    )
    
    assert results == fake_models
    base_service.repository.get_multi.assert_called_once_with(
        mock_session,
        skip=10,
        limit=20,
        filters=filters,
        order_by=order_by
    )

@pytest.mark.asyncio
async def test_create(base_service, mock_session):
    fake_model = FakeModel()
    base_service.repository.create.return_value = fake_model
    obj_in = {"name": "test"}
    
    result = await base_service.create(mock_session, obj_in=obj_in)
    

    assert result == fake_model
    base_service.repository.create.assert_called_once_with(mock_session, obj_in=obj_in)

@pytest.mark.asyncio
async def test_update(base_service, mock_session):

    fake_model = FakeModel()
    base_service.repository.update.return_value = fake_model
    obj_in = {"name": "updated"}
    

    result = await base_service.update(mock_session, id=1, obj_in=obj_in)
    
    # Verificar
    assert result == fake_model
    base_service.repository.update.assert_called_once_with(mock_session, id=1, obj_in=obj_in)

@pytest.mark.asyncio
async def test_delete(base_service, mock_session):
    base_service.repository.delete.return_value = True
    
    result = await base_service.delete(mock_session, id=1)
    
    assert result is True
    base_service.repository.delete.assert_called_once_with(mock_session, id=1)

@pytest.mark.asyncio
async def test_get_not_found(base_service, mock_session):
    base_service.repository.get.return_value = None
    
    result = await base_service.get(mock_session, id=999)
    
    assert result is None
    base_service.repository.get.assert_called_once_with(mock_session, 999)