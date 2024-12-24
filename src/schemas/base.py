from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BaseResponseSchema(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True