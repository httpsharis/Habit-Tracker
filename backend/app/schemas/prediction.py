"""
NeuroHabit Prediction Schemas.

Pydantic models for direct prediction API endpoints.
"""
from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    """
    Input schema for direct /api/predict endpoint (bypasses chat flow).
    
    Attributes:
        sleep_hours: Hours of sleep (0-24).
        work_intensity: Subjective work intensity rating (1-10).
        stress_level: Subjective stress rating (1-10).
        mood_score: Subjective mood rating (1-10).
    """
    sleep_hours: float = Field(..., ge=0, le=24, description="Sleep duration in hours")
    work_intensity: float = Field(..., ge=1, le=10, description="Work intensity (1-10)")
    stress_level: float = Field(..., ge=1, le=10, description="Stress level (1-10)")
    mood_score: float = Field(..., ge=1, le=10, description="Mood score (1-10)")


class PredictionResponse(BaseModel):
    """
    Response schema for prediction results.
    
    Attributes:
        daily_score: Predicted performance score (0-100).
        day_classification: "Attack Mode" or "Recovery Mode".
        persona: User persona based on clustering.
        recommendations: List of actionable strategic directives.
    """
    daily_score: float = Field(..., description="Performance index (0-100)")
    day_classification: str = Field(..., description="Attack Mode or Recovery Mode")
    persona: str = Field(..., description="Detected persona type")
    recommendations: list[str] = Field(..., description="Strategic directives")
