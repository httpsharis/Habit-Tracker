"""
HabitOS Session Model.

Stores each habit tracking session with all 6 metrics and ML predictions.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class HabitSession(Base):
    """
    Habit tracking session entity.
    
    Records all 6 biometric inputs and ML prediction outputs for each session.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        
        # Input Metrics (6 total)
        sleep_hours: Hours of sleep (0-24)
        work_intensity: Work/study intensity (1-10)
        stress_level: Current stress level (1-10)
        mood_score: Psychological state (1-10)
        screen_time: Hours of screen time (0-24)
        hydration: Glasses of water consumed (0-20)
        
        # ML Predictions
        daily_score: Calculated performance score (0-100)
        day_classification: Attack Mode or Recovery Mode
        persona: Assigned persona type
        
        created_at: Session timestamp
    """
    __tablename__ = "habit_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Input Metrics
    sleep_hours = Column(Float, nullable=False)
    work_intensity = Column(Float, nullable=False)
    stress_level = Column(Float, nullable=False)
    mood_score = Column(Float, nullable=False)
    screen_time = Column(Float, nullable=True, default=0.0)  # New metric
    hydration = Column(Float, nullable=True, default=0.0)     # New metric
    
    # ML Predictions
    daily_score = Column(Float, nullable=False)
    day_classification = Column(String(50), nullable=False)
    persona = Column(String(100), nullable=False)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship to user
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<HabitSession(id={self.id}, user_id={self.user_id}, score={self.daily_score})>"
    
    def to_dict(self):
        """Convert session to dictionary for analysis."""
        return {
            "id": self.id,
            "sleep_hours": self.sleep_hours,
            "work_intensity": self.work_intensity,
            "stress_level": self.stress_level,
            "mood_score": self.mood_score,
            "screen_time": self.screen_time,
            "hydration": self.hydration,
            "daily_score": self.daily_score,
            "day_classification": self.day_classification,
            "persona": self.persona,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
