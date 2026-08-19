from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    genres = Column(JSON, default=list)        # e.g. ["Action", "Science Fiction"]
    duration = Column(JSON, default=list)      # e.g. ["medium", "short"]
    release_year = Column(JSON, default=list)  # e.g. ["2020-2023", "classics"]
    onboarding_completed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="preference")
