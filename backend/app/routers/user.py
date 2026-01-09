"""
HabitOS User Router.

API endpoints for user management, history, and statistics.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.session import HabitSession
from app.schemas import (
    UserCreate, UserResponse,
    SessionListResponse, SessionResponse,
    UserStatsResponse
)

router = APIRouter()


# ============================================================================
# USER ENDPOINTS
# ============================================================================

@router.post("/user", response_model=UserResponse)
def create_or_get_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user or get existing user by username.
    
    This endpoint is idempotent - calling with the same username
    will return the existing user rather than creating a duplicate.
    """
    # Check if user exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        return existing_user
    
    # Create new user
    new_user = User(username=user_data.username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/user/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ============================================================================
# HISTORY ENDPOINTS
# ============================================================================

@router.get("/user/{user_id}/history", response_model=SessionListResponse)
def get_user_history(
    user_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get user's habit session history.
    
    Returns paginated list of past sessions, ordered by most recent.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get total count
    total = db.query(func.count(HabitSession.id))\
        .filter(HabitSession.user_id == user_id).scalar()
    
    # Get sessions
    sessions = db.query(HabitSession)\
        .filter(HabitSession.user_id == user_id)\
        .order_by(HabitSession.created_at.desc())\
        .offset(offset)\
        .limit(limit)\
        .all()
    
    return SessionListResponse(total=total, sessions=sessions)


# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

def calculate_trend(recent_avg: Optional[float], overall_avg: float) -> str:
    """Calculate trend based on recent vs overall average."""
    if recent_avg is None or overall_avg == 0:
        return "↔ stable"
    
    diff_percent = ((recent_avg - overall_avg) / overall_avg) * 100
    
    if diff_percent > 5:
        return "↑ improving"
    elif diff_percent < -5:
        return "↓ declining"
    else:
        return "↔ stable"


@router.get("/user/{user_id}/stats", response_model=UserStatsResponse)
def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    """
    Get user's statistics and trends.
    
    Calculates averages for all metrics and compares recent (7 days)
    to overall performance to identify trends.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all sessions
    sessions = db.query(HabitSession)\
        .filter(HabitSession.user_id == user_id).all()
    
    if not sessions:
        return UserStatsResponse(
            user_id=user_id,
            total_sessions=0,
            avg_sleep=0, avg_work_intensity=0, avg_stress=0,
            avg_mood=0, avg_screen_time=0, avg_hydration=0,
            avg_daily_score=0
        )
    
    # Calculate overall averages
    total = len(sessions)
    avg_sleep = sum(s.sleep_hours for s in sessions) / total
    avg_work = sum(s.work_intensity for s in sessions) / total
    avg_stress = sum(s.stress_level for s in sessions) / total
    avg_mood = sum(s.mood_score for s in sessions) / total
    avg_screen = sum(s.screen_time or 0 for s in sessions) / total
    avg_hydration = sum(s.hydration or 0 for s in sessions) / total
    avg_score = sum(s.daily_score for s in sessions) / total
    
    # Calculate recent averages (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_sessions = [s for s in sessions if s.created_at >= seven_days_ago]
    
    recent_avg_sleep = None
    recent_avg_work = None
    recent_avg_stress = None
    recent_avg_mood = None
    recent_avg_screen = None
    recent_avg_hydration = None
    recent_avg_score = None
    
    if recent_sessions:
        r_total = len(recent_sessions)
        recent_avg_sleep = sum(s.sleep_hours for s in recent_sessions) / r_total
        recent_avg_work = sum(s.work_intensity for s in recent_sessions) / r_total
        recent_avg_stress = sum(s.stress_level for s in recent_sessions) / r_total
        recent_avg_mood = sum(s.mood_score for s in recent_sessions) / r_total
        recent_avg_screen = sum(s.screen_time or 0 for s in recent_sessions) / r_total
        recent_avg_hydration = sum(s.hydration or 0 for s in recent_sessions) / r_total
        recent_avg_score = sum(s.daily_score for s in recent_sessions) / r_total
    
    # Calculate trends
    # For stress, lower is better, so invert the trend
    sleep_trend = calculate_trend(recent_avg_sleep, avg_sleep)
    stress_trend_raw = calculate_trend(recent_avg_stress, avg_stress)
    # Invert stress trend (lower stress = improving)
    if stress_trend_raw == "↑ improving":
        stress_trend = "↓ increasing"
    elif stress_trend_raw == "↓ declining":
        stress_trend = "↑ decreasing"
    else:
        stress_trend = "↔ stable"
    
    mood_trend = calculate_trend(recent_avg_mood, avg_mood)
    score_trend = calculate_trend(recent_avg_score, avg_score)
    
    return UserStatsResponse(
        user_id=user_id,
        total_sessions=total,
        avg_sleep=round(avg_sleep, 2),
        avg_work_intensity=round(avg_work, 2),
        avg_stress=round(avg_stress, 2),
        avg_mood=round(avg_mood, 2),
        avg_screen_time=round(avg_screen, 2),
        avg_hydration=round(avg_hydration, 2),
        avg_daily_score=round(avg_score, 2),
        recent_avg_sleep=round(recent_avg_sleep, 2) if recent_avg_sleep else None,
        recent_avg_work_intensity=round(recent_avg_work, 2) if recent_avg_work else None,
        recent_avg_stress=round(recent_avg_stress, 2) if recent_avg_stress else None,
        recent_avg_mood=round(recent_avg_mood, 2) if recent_avg_mood else None,
        recent_avg_screen_time=round(recent_avg_screen, 2) if recent_avg_screen else None,
        recent_avg_hydration=round(recent_avg_hydration, 2) if recent_avg_hydration else None,
        recent_avg_daily_score=round(recent_avg_score, 2) if recent_avg_score else None,
        sleep_trend=sleep_trend,
        stress_trend=stress_trend,
        mood_trend=mood_trend,
        score_trend=score_trend
    )
