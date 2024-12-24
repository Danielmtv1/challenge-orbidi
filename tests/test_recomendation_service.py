from unittest.mock import AsyncMock
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from src.core.config import Settings
from src.services.recomendation import RecommendationService, LocationCategoryService 

# Mock models
class MockExplorationRecommendation:
    def __init__(self, location_id=None, location_name=None, category_id=None, category_name=None, last_reviewed_at=None):
        self.location_id = location_id
        self.location_name = location_name
        self.category_id = category_id
        self.category_name = category_name
        self.last_reviewed_at = last_reviewed_at

class MockLocationCategoryReview:
    def __init__(self, location_id=None, category_id=None, last_reviewed_at=None):
        self.location_id = location_id
        self.category_id = category_id
        self.last_reviewed_at = last_reviewed_at

class MockLocation:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

class MockCategory:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

# Mock repositories
class MockRecommendationRepository:
    async def get_exploration_recommendations(self, db, limit):
        pass

    async def record_review(self, db, location_id, category_id):
        pass

class MockLocationCategoryRepository:
    async def create_relationship(self, session, location_id, category_id):
        pass

    async def update_last_view(self, session, location_id):
        pass

@pytest.fixture
def mock_recommendation_repository():
    repository = MockRecommendationRepository()
    for method in ['get_exploration_recommendations', 'record_review']:
        setattr(repository, method, AsyncMock())
    return repository

@pytest.fixture
def mock_location_category_repository():
    repository = MockLocationCategoryRepository()
    for method in ['create_relationship', 'update_last_view']:
        setattr(repository, method, AsyncMock())
    return repository

@pytest.fixture
def recommendation_service(mock_recommendation_repository):
    service = RecommendationService()
    service.repository = mock_recommendation_repository
    return service

@pytest.fixture
def location_category_service(mock_location_category_repository):
    service = LocationCategoryService()
    service.repository = mock_location_category_repository
    return service

@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def mock_settings():
    settings = Settings()
    settings.REVIEW_EXPIRATION_DAYS = 30
    return settings

@pytest.fixture
def sample_exploration_recommendations():
    return [
        MockExplorationRecommendation(
            location_id=1,
            location_name="Location 1",
            category_id=1,
            category_name="Category 1",
            last_reviewed_at=datetime.now() - timedelta(days=35)
        ),
        MockExplorationRecommendation(
            location_id=2,
            location_name="Location 2",
            category_id=2,
            category_name="Category 2",
            last_reviewed_at=None
        )
    ]

@pytest.fixture
def sample_location_category_review():
    return MockLocationCategoryReview(
        location_id=1,
        category_id=1,
        last_reviewed_at=datetime.now()
    )

@pytest.fixture
def sample_location():
    return MockLocation(id=1, name="Location 1")

@pytest.fixture
def sample_category():
    return MockCategory(id=1, name="Category 1")


# Test successful retrieval of exploration recommendations
@pytest.mark.asyncio
async def test_get_exploration_recommendations_success(
    recommendation_service,
    mock_session,
    sample_exploration_recommendations,
    mock_settings
):
    # Configure mock
    recommendation_service.repository.get_exploration_recommendations.return_value = sample_exploration_recommendations

    # Execute
    result = await recommendation_service.get_exploration_recommendations(
        session=mock_session,
        limit=10
    )

    # Assert
    assert result == sample_exploration_recommendations
    recommendation_service.repository.get_exploration_recommendations.assert_called_once_with(db=mock_session, limit=10)

# Test error during exploration recommendations retrieval
@pytest.mark.asyncio
async def test_get_exploration_recommendations_error(recommendation_service, mock_session):
    # Configure mock to raise error
    recommendation_service.repository.get_exploration_recommendations.side_effect = HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error getting exploration recommendations"
            )

    # Assert
    with pytest.raises(HTTPException) as exc_info:
        await recommendation_service.get_exploration_recommendations(
            session=mock_session,
            limit=10
        )
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error getting exploration recommendations" in exc_info.value.detail

# Test successful recording of review
@pytest.mark.asyncio
async def test_record_review_success(
    recommendation_service,
    mock_session
):
    # Configure mock
    recommendation_service.repository.record_review.return_value = None

    # Execute
    await recommendation_service.record_review(
        session=mock_session,
        location_id=1,
        category_id=1
    )

    # Assert
    recommendation_service.repository.record_review.assert_called_once_with(
        db=mock_session,
        location_id=1,
        category_id=1
    )

# Test error during review recording
@pytest.mark.asyncio
async def test_record_review_error(recommendation_service, mock_session):
    # Configure mock to raise error
    recommendation_service.repository.record_review.side_effect = HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error recording review"
            )

    # Assert
    with pytest.raises(HTTPException) as exc_info:
        await recommendation_service.record_review(
            session=mock_session,
            location_id=1,
            category_id=1
        )
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error recording review" in exc_info.value.detail

# Test successful creation of location-category relationship
@pytest.mark.asyncio
async def test_create_category_relationship_success(
    location_category_service,
    mock_session,
    sample_location_category_review
):
    # Configure mock
    location_category_service.repository.create_relationship.return_value = sample_location_category_review

    # Execute
    result = await location_category_service.create_category_relationship(
        session=mock_session,
        location_id=1,
        category_id=1
    )

    # Assert
    assert result == sample_location_category_review
    location_category_service.repository.create_relationship.assert_called_once_with(
        session=mock_session,
        location_id=1,
        category_id=1
    )

# Test error during creation of location-category relationship
@pytest.mark.asyncio
async def test_create_category_relationship_error(location_category_service, mock_session):
    # Configure mock to raise error
    location_category_service.repository.create_relationship.side_effect = SQLAlchemyError("Database error")

    # Assert
    with pytest.raises(HTTPException) as exc_info:
        await location_category_service.create_category_relationship(
            session=mock_session,
            location_id=1,
            category_id=1
        )
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error creating location-category relationship" in exc_info.value.detail

# Test successful update of location view
@pytest.mark.asyncio
async def test_update_location_view_success(
    location_category_service,
    mock_session,
    sample_location_category_review
):
    # Configure mock
    location_category_service.repository.update_last_view.return_value = sample_location_category_review

    # Execute
    result = await location_category_service.update_location_view(
        session=mock_session,
        location_id=1
    )

    # Assert
    assert result == sample_location_category_review
    location_category_service.repository.update_last_view.assert_called_once_with(
        session=mock_session,
        location_id=1
    )

# Test error during update of location view
@pytest.mark.asyncio
async def test_update_location_view_error(location_category_service, mock_session):
    # Configure mock to raise error
    location_category_service.repository.update_last_view.side_effect = SQLAlchemyError("Database error")

    # Assert
    with pytest.raises(HTTPException) as exc_info:
        await location_category_service.update_location_view(
            session=mock_session,
            location_id=1
        )
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error updating location view" in exc_info.value.detail