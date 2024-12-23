from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.schemas.recomendation import ExplorationRecommendation
from src.services.recomendation import RecommendationService
from src.api.dependencies import get_recommendation_service

router = APIRouter()

@router.get("/explore", response_model=List[ExplorationRecommendation])
async def get_exploration_recommendations(
    limit: int = Query(default=10, ge=1, le=50),
    db:AsyncSession = Depends(get_db),

):
    
    recommendation_service = RecommendationService()

    try:
        recommendations = await recommendation_service.get_exploration_recommendations(
            db=db,
            limit=limit
        )
        
        return [
            ExplorationRecommendation(
                location_id=location.id,
                category_id=category.id,
                location_name=location.name,
                category_name=category.name,
                last_reviewed_at=last_reviewed,
                distance_km=None
            )
            for location, category, last_reviewed in recommendations
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendations: {str(e)}"
        )
