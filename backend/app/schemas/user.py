"""
HabitOS User Schemas.

Pydantic models for user management API.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserCreate(BaseModel):
    """Schema for creating or looking up a user."""
    username: str = Field(..., min_length=2, max_length=100, description="Unique username")


class UserResponse(BaseModel):
    """Schema for user API responses."""
    id: int
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# SESSION SCHEMAS
# ============================================================================

class SessionCreate(BaseModel):
    """Schema for creating a new habit session."""
    user_id: int = Field(..., description="User ID")
    sleep_hours: float = Field(..., ge=0, le=24, description="Hours slept")
    work_intensity: float = Field(..., ge=1, le=10, description="Work intensity 1-10")
    stress_level: float = Field(..., ge=1, le=10, description="Stress level 1-10")
    mood_score: float = Field(..., ge=1, le=10, description="Mood score 1-10")
    screen_time: Optional[float] = Field(0.0, ge=0, le=24, description="Screen time hours")
    hydration: Optional[float] = Field(0.0, ge=0, le=20, description="Glasses of water")
    daily_score: float = Field(..., description="Calculated daily score")
    day_classification: str = Field(..., description="Attack/Recovery mode")
    persona: str = Field(..., description="Assigned persona")


class SessionResponse(BaseModel):
    """Schema for session API responses."""
    id: int
    user_id: int
    sleep_hours: float
    work_intensity: float
    stress_level: float
    mood_score: float
    screen_time: float
    hydration: float
    daily_score: float
    day_classification: str
    persona: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Schema for paginated session list."""
    total: int
    sessions: List[SessionResponse]


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================

class UserStatsResponse(BaseModel):
    """
    User statistics and trends.
    
    Provides averages and trends based on historical data.
    """
    user_id: int
    total_sessions: int
    
    # Averages (all time)
    avg_sleep: float
    avg_work_intensity: float
    avg_stress: float
    avg_mood: float
    avg_screen_time: float
    avg_hydration: float
    avg_daily_score: float
    
    # Recent averages (last 7 days)
    recent_avg_sleep: Optional[float] = None
    recent_avg_work_intensity: Optional[float] = None
    recent_avg_stress: Optional[float] = None
    recent_avg_mood: Optional[float] = None
    recent_avg_screen_time: Optional[float] = None
    recent_avg_hydration: Optional[float] = None
    recent_avg_daily_score: Optional[float] = None
    
    # Trends (positive = improving)
    sleep_trend: Optional[str] = None      # "↑ improving", "↓ declining", "↔ stable"
    stress_trend: Optional[str] = None
    mood_trend: Optional[str] = None
    score_trend: Optional[str] = None
