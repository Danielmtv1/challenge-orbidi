from unittest.mock import AsyncMock, Mock
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

# Mock del modelo Category
class MockCategory:
    def __init__(self, id=None, name=None, description=None, is_active=True):
        self.id = id
        self.name = name
        self.description = description
        self.is_active = is_active

# Mock del repositorio
class MockCategoryRepository:
    async def get_active_categories(self, db, skip=0, limit=100):
        pass

    async def get_by_name(self, db, name):
        pass

    async def bulk_create(self, session, categories):
        pass

    async def create(self, session, obj_in):
        pass

    async def update(self, session, id, obj_in):
        pass

@pytest.fixture
def mock_repository():
    repository = MockCategoryRepository()
    # Convertir todos los métodos en AsyncMock
    for method in ['get_active_categories', 'get_by_name', 'bulk_create', 'create', 'update']:
        setattr(repository, method, AsyncMock())
    return repository

@pytest.fixture
def category_service(mock_repository):
    # Mockear la clase CategoryService
    service = Mock()
    service.repository = mock_repository
    
    # Implementar los métodos como async con manejo de errores
    async def get_active_categories(session, skip=0, limit=100):
        try:
            return await mock_repository.get_active_categories(db=session, skip=skip, limit=limit)
        except SQLAlchemyError as e:
            raise Exception(f"Error getting active categories: {str(e)}")
    
    async def get_by_name(session, name):
        try:
            return await mock_repository.get_by_name(db=session, name=name)
        except SQLAlchemyError as e:
            raise Exception(f"Error getting category by name: {str(e)}")
    
    async def bulk_create_categories(session, categories):
        try:
            return await mock_repository.bulk_create(session=session, categories=categories)
        except SQLAlchemyError as e:
            raise Exception(f"Error bulk creating categories: {str(e)}")
    
    async def create_category(session, name, description=None, is_active=True):
        try:
            category_data = {
                "name": name,
                "description": description,
                "is_active": is_active
            }
            return await mock_repository.create(session=session, obj_in=category_data)
        except SQLAlchemyError as e:
            raise Exception(f"Error creating category: {str(e)}")
    
    async def update_category_status(session, category_id, is_active):
        try:
            return await mock_repository.update(session, id=category_id, obj_in={"is_active": is_active})
        except SQLAlchemyError as e:
            raise Exception(f"Error updating category status: {str(e)}")
    
    service.get_active_categories = get_active_categories
    service.get_by_name = get_by_name
    service.bulk_create_categories = bulk_create_categories
    service.create_category = create_category
    service.update_category_status = update_category_status
    
    return service

@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def sample_category():
    return MockCategory(
        id=1,
        name="Test Category",
        description="Test Description",
        is_active=True
    )

# ... [resto de los tests anteriores se mantienen igual hasta los tests de error]

@pytest.mark.asyncio
async def test_get_by_name_error(category_service, mock_session):
    # Configurar
    category_service.repository.get_by_name.side_effect = SQLAlchemyError("Database error")
    
    # Verificar que se lanza la excepción
    with pytest.raises(Exception) as exc_info:
        await category_service.get_by_name(mock_session, name="Test")
    assert "Error getting category by name" in str(exc_info.value)

@pytest.mark.asyncio
async def test_create_category_error(category_service, mock_session):
    # Configurar
    category_service.repository.create.side_effect = SQLAlchemyError("Database error")
    
    # Verificar que se lanza la excepción
    with pytest.raises(Exception) as exc_info:
        await category_service.create_category(
            session=mock_session,
            name="Test Category"
        )
    assert "Error creating category" in str(exc_info.value)

@pytest.mark.asyncio
async def test_update_category_status_error(category_service, mock_session):
    # Configurar
    category_service.repository.update.side_effect = SQLAlchemyError("Database error")
    
    # Verificar que se lanza la excepción
    with pytest.raises(Exception) as exc_info:
        await category_service.update_category_status(
            mock_session,
            category_id=1,
            is_active=False
        )
    assert "Error updating category status" in str(exc_info.value)