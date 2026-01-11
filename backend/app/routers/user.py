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
    Get user's statistics and trends using optimized SQL aggregation.
    
    Efficiently calculates overall and recent (7-day) averages directly in the DB.
    """
    # Verify user exists (lightweight query)
    if not db.query(User.id).filter(User.id == user_id).scalar():
        raise HTTPException(status_code=404, detail="User not found")
    
    # 1. Calculate OVERALL averages
    overall_stats = db.query(
        func.count(HabitSession.id).label("total"),
        func.avg(HabitSession.sleep_hours).label("avg_sleep"),
        func.avg(HabitSession.work_intensity).label("avg_work"),
        func.avg(HabitSession.stress_level).label("avg_stress"),
        func.avg(HabitSession.mood_score).label("avg_mood"),
        func.avg(HabitSession.screen_time).label("avg_screen"),
        func.avg(HabitSession.hydration).label("avg_hydration"),
        func.avg(HabitSession.daily_score).label("avg_score")
    ).filter(HabitSession.user_id == user_id).first()
    
    if not overall_stats.total:
        return UserStatsResponse(
            user_id=user_id, total_sessions=0,
            avg_sleep=0, avg_work_intensity=0, avg_stress=0,
            avg_mood=0, avg_screen_time=0, avg_hydration=0,
            avg_daily_score=0
        )
    
    # 2. Calculate RECENT averages (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_stats = db.query(
        func.avg(HabitSession.sleep_hours).label("avg_sleep"),
        func.avg(HabitSession.work_intensity).label("avg_work"),
        func.avg(HabitSession.stress_level).label("avg_stress"),
        func.avg(HabitSession.mood_score).label("avg_mood"),
        func.avg(HabitSession.screen_time).label("avg_screen"),
        func.avg(HabitSession.hydration).label("avg_hydration"),
        func.avg(HabitSession.daily_score).label("avg_score")
    ).filter(
        HabitSession.user_id == user_id,
        HabitSession.created_at >= seven_days_ago
    ).first()
    
    # Helper to clean nullable floats
    def val(v): return round(v, 2) if v is not None else 0.0
    def r_val(v): return round(v, 2) if v is not None else None  # Recent can be None

    # 3. Calculate Trends
    # Handle case where recent_stats contains None values (if no recent data)
    r_sleep = recent_stats.avg_sleep if recent_stats and recent_stats.avg_sleep is not None else 0
    r_stress = recent_stats.avg_stress if recent_stats and recent_stats.avg_stress is not None else 0
    r_mood = recent_stats.avg_mood if recent_stats and recent_stats.avg_mood is not None else 0
    r_score = recent_stats.avg_score if recent_stats and recent_stats.avg_score is not None else 0
    
    # Helper for trend formatting
    def format_recent(val):
        return round(val, 2) if val is not None else None

    # Sleep Trend
    sleep_trend = calculate_trend(r_sleep, overall_stats.avg_sleep or 0)
    
    # Stress Trend (inverted logic)
    stress_raw = calculate_trend(r_stress, overall_stats.avg_stress or 0)
    if stress_raw == "↑ improving": stress_trend = "↓ increasing"
    elif stress_raw == "↓ declining": stress_trend = "↑ decreasing"
    else: stress_trend = "↔ stable"
    
    mood_trend = calculate_trend(r_mood, overall_stats.avg_mood or 0)
    score_trend = calculate_trend(r_score, overall_stats.avg_score or 0)
    
    return UserStatsResponse(
        user_id=user_id,
        total_sessions=overall_stats.total,
        avg_sleep=val(overall_stats.avg_sleep),
        avg_work_intensity=val(overall_stats.avg_work),
        avg_stress=val(overall_stats.avg_stress),
        avg_mood=val(overall_stats.avg_mood),
        avg_screen_time=val(overall_stats.avg_screen),
        avg_hydration=val(overall_stats.avg_hydration),
        avg_daily_score=val(overall_stats.avg_score),
        
        recent_avg_sleep=format_recent(recent_stats.avg_sleep) if recent_stats else None,
        recent_avg_work_intensity=format_recent(recent_stats.avg_work) if recent_stats else None,
        recent_avg_stress=format_recent(recent_stats.avg_stress) if recent_stats else None,
        recent_avg_mood=format_recent(recent_stats.avg_mood) if recent_stats else None,
        recent_avg_screen_time=format_recent(recent_stats.avg_screen) if recent_stats else None,
        recent_avg_hydration=format_recent(recent_stats.avg_hydration) if recent_stats else None,
        recent_avg_daily_score=format_recent(recent_stats.avg_score) if recent_stats else None,
        
        sleep_trend=sleep_trend,
        stress_trend=stress_trend,
        mood_trend=mood_trend,
        score_trend=score_trend
    )
