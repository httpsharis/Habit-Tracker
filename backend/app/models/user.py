"""
HabitOS User Model.

Stores user information for personalized tracking.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """
    User entity for HabitOS.
    
    Each user has unique data and personalized tracking history.
    
    Attributes:
        id: Primary key
        username: Unique identifier for the user
        created_at: Account creation timestamp
        sessions: Relationship to user's habit sessions
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to sessions
    sessions = relationship("HabitSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
