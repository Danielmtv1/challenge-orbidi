from sqlalchemy import Column, Float, String, Index
from sqlalchemy.orm import relationship
from .base import BaseModel
from geoalchemy2 import Geometry

class Location(BaseModel):
    __tablename__ = "locations"
    
    name = Column(String, nullable=False)
    description = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    point = Column(Geometry(geometry_type='POINT', srid=4326))
    
    reviews = relationship("LocationCategoryReview", back_populates="location")
    
    __table_args__ = (
        Index('idx_locations_point', 'point', postgresql_using='gist'),
    )
