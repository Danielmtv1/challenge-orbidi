from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.recomendation import ExplorationRecommendation
from src.repositories.recomendation import RecommendationRepository


router = APIRouter()

@router.get("/explore", response_model=List[ExplorationRecommendation])
async def get_exploration_recommendations(
    limit: int = Query(default=10, ge=1, le=50),
    db:AsyncSession = Depends(get_db),

):
    
    recommendation_repo = RecommendationRepository()

    try:
        # Obtener los datos originales
        raw_recommendations = await recommendation_repo.get_exploration_recommendations(
            db=db,
            limit=limit
        )

        # Transformar los datos en el formato esperado

        
        return raw_recommendations
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))