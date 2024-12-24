from pydantic import BaseModel, Field, field_validator
from typing import Optional
from .base import BaseResponseSchema


class LocationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class LocationCreate(LocationBase):
    @field_validator('latitude', 'longitude')
    def round_coordinates(cls, v):
        """ Round the coordinates to 6 decimal places """
        return round(float(v), 6)

class LocationResponse(LocationBase, BaseResponseSchema):
    pass

class LocationWithDistance(LocationResponse):
    distance_km: Optional[float] = Field(None, ge=0)