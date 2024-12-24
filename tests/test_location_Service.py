from unittest.mock import AsyncMock, Mock
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

# Mock models
class MockLocation:
    def __init__(self, id=None, name=None, latitude=None, longitude=None, description=None):
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.description = description

class MockLocationWithDistance(MockLocation):
    def __init__(self, distance=None, **kwargs):
        super().__init__(**kwargs)
        self.distance = distance

# Mock repositories
class MockLocationRepository:
    async def create_with_coordinates(self, session, name, latitude, longitude, description):
        pass

    async def get_nearby(self, session, latitude, longitude, radius_km, limit):
        pass

class MockLocationCategoryRepository:
    async def create_relationship(self, session, location_id, category_id):
        pass
    
    async def update_last_view(self, session, location_id):
        pass

@pytest.fixture
def mock_location_repository():
    repository = MockLocationRepository()
    for method in ['create_with_coordinates', 'get_nearby']:
        setattr(repository, method, AsyncMock())
    return repository

@pytest.fixture
def mock_category_repository():
    repository = MockLocationCategoryRepository()
    for method in ['create_relationship', 'update_last_view']:
        setattr(repository, method, AsyncMock())
    return repository

@pytest.fixture
def location_service(mock_location_repository, mock_category_repository):
    service = Mock()
    service.location_repository = mock_location_repository
    service.category_repository = mock_category_repository

    async def create_location(session, name, latitude, longitude, category, description=None):
        try:
            location = await mock_location_repository.create_with_coordinates(
                session=session,
                name=name,
                latitude=latitude,
                longitude=longitude,
                description=description
            )
            
            category_relationship = await mock_category_repository.create_relationship(
                session=session,
                location_id=location.id,
                category_id=category
            )
            
            if not category_relationship:
                raise Exception("Error creando la relación entre la ubicación y la categoría")
                
            return location
            
        except SQLAlchemyError as e:
            raise Exception(f"Error creating location: {str(e)}")

    async def get_nearby_locations(session, latitude, longitude, radius_km, limit):
        try:
            locations = await mock_location_repository.get_nearby(
                session=session,
                latitude=latitude,
                longitude=longitude,
                radius_km=radius_km,
                limit=limit
            )
            
            for location in locations:
                await mock_category_repository.update_last_view(
                    session=session,
                    location_id=location.id
                )
                
            return locations
            
        except SQLAlchemyError as e:
            raise Exception(f"Error retrieving nearby locations: {str(e)}")

    service.create_location = create_location
    service.get_nearby_locations = get_nearby_locations
    
    return service

@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def sample_location():
    return MockLocation(
        id=1,
        name="Test Location",
        latitude=40.7128,
        longitude=-74.0060,
        description="Test Description"
    )

@pytest.fixture
def sample_locations_with_distance():
    return [
        MockLocationWithDistance(
            id=1,
            name="Location 1",
            latitude=40.7128,
            longitude=-74.0060,
            distance=1.5
        ),
        MockLocationWithDistance(
            id=2,
            name="Location 2",
            latitude=40.7129,
            longitude=-74.0061,
            distance=2.0
        )
    ]

# Test successful creation of location
@pytest.mark.asyncio
async def test_create_location_success(
    location_service,
    mock_session,
    sample_location
):
    # Configure mocks
    location_service.location_repository.create_with_coordinates.return_value = sample_location
    location_service.category_repository.create_relationship.return_value = True

    # Execute
    result = await location_service.create_location(
        session=mock_session,
        name="Test Location",
        latitude=40.7128,
        longitude=-74.0060,
        category=1,
        description="Test Description"
    )

    # Assert
    assert result == sample_location
    location_service.location_repository.create_with_coordinates.assert_called_once()
    location_service.category_repository.create_relationship.assert_called_once()

# Test failed relationship creation
@pytest.mark.asyncio
async def test_create_location_failed_relationship(
    location_service,
    mock_session,
    sample_location
):
    # Configure mocks
    location_service.location_repository.create_with_coordinates.return_value = sample_location
    location_service.category_repository.create_relationship.return_value = False

    # Assert
    with pytest.raises(Exception) as exc_info:
        await location_service.create_location(
            session=mock_session,
            name="Test Location",
            latitude=40.7128,
            longitude=-74.0060,
            category=1
        )
    assert "Error creando la relación" in str(exc_info.value)

# Test successful nearby locations retrieval
@pytest.mark.asyncio
async def test_get_nearby_locations_success(
    location_service,
    mock_session,
    sample_locations_with_distance
):
    # Configure mocks
    location_service.location_repository.get_nearby.return_value = sample_locations_with_distance
    location_service.category_repository.update_last_view.return_value = None

    # Execute
    result = await location_service.get_nearby_locations(
        session=mock_session,
        latitude=40.7128,
        longitude=-74.0060,
        radius_km=5.0,
        limit=10
    )

    # Assert
    assert result == sample_locations_with_distance
    location_service.location_repository.get_nearby.assert_called_once()
    assert location_service.category_repository.update_last_view.call_count == len(sample_locations_with_distance)

# Test database error in nearby locations retrieval
@pytest.mark.asyncio
async def test_get_nearby_locations_error(location_service, mock_session):
    # Configure mock to raise error
    location_service.location_repository.get_nearby.side_effect = SQLAlchemyError("Database error")

    # Assert
    with pytest.raises(Exception) as exc_info:
        await location_service.get_nearby_locations(
            session=mock_session,
            latitude=40.7128,
            longitude=-74.0060,
            radius_km=5.0,
            limit=10
        )
    assert "Error retrieving nearby locations" in str(exc_info.value)