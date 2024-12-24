from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class ExplorationRecommendation(BaseModel):
    location_id: int
    location_name: str
    category_id: int
    category_name: str
    last_reviewed_at: Optional[datetime]
