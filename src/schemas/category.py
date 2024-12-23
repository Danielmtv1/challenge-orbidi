from pydantic import BaseModel, Field
from typing import Optional
from .base import BaseResponseSchema

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    is_active: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase, BaseResponseSchema):
    pass