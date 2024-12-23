from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db

from src.schemas.category import CategoryCreate, CategoryResponse
from src.repositories.category import CategoryRepository
from src.api.dependencies import get_category_repository, verify_api_key

router = APIRouter()

@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=201,
    dependencies=[Depends(verify_api_key)]
)
async def create_category(
    category_in: CategoryCreate,
    db: AsyncSession = Depends(get_db),

):
    """
    Create a new category
    """
    category_data = {
        "name": category_in.name,
        "description": category_in.description
    }
    category_repo = CategoryRepository()
    category = await category_repo.create(session=db, obj_in=category_data)
    return category


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):

    category_repo = CategoryRepository()
    category =  await category_repo.get_active_categories(db=session, skip=skip, limit=limit)
    return category