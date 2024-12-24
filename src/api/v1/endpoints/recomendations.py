from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.recomendation import ExplorationRecommendation
from src.repositories.recomendation import RecommendationRepository
from src.services.recomendation import RecommendationService


router = APIRouter()

@router.get("/explore", response_model=List[ExplorationRecommendation])
async def get_exploration_recommendations(
    limit: int = Query(default=10, ge=1, le=50),
    db:AsyncSession = Depends(get_db),

):
    
    recommendation_service = RecommendationService()

    try:
        raw_recommendations = await recommendation_service.get_exploration_recommendations(
            session=db,
            limit=limit
        )
      
        return raw_recommendations
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))