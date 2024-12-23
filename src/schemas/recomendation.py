from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ExplorationRecommendation(BaseModel):
    location_id: int
    category_id: int
    location_name: str
    category_name: str
    last_reviewed_at: Optional[datetime]
    distance_km: Optional[float] = Field(None, ge=0)