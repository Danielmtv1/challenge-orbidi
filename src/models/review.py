from sqlalchemy import Column, ForeignKey, DateTime, Index, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel

class LocationCategoryReview(BaseModel):
    __tablename__ = "location_category_reviews"
    
    location_id = Column(
        Integer,
        ForeignKey("locations.id", ondelete="CASCADE"),
        nullable=False
    )
    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False
    )
    last_reviewed_at = Column(DateTime(timezone=True), nullable=False)
    
    location = relationship("Location", back_populates="reviews")
    category = relationship("Category", back_populates="reviews")
    
    __table_args__ = (
        Index(
            'idx_location_category_last_reviewed',
            'location_id',
            'category_id',
            'last_reviewed_at'
        ),
    )
