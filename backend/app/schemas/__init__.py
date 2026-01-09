"""
HabitOS Schemas Package.

Exports all Pydantic models for API validation.
"""
from app.schemas.chat import ChatInput, ChatResponse
from app.schemas.prediction import PredictionInput, PredictionResponse
from app.schemas.user import (
    UserCreate, UserResponse,
    SessionCreate, SessionResponse, SessionListResponse,
    UserStatsResponse
)

__all__ = [
    "ChatInput",
    "ChatResponse",
    "PredictionInput",
    "PredictionResponse",
    "UserCreate",
    "UserResponse",
    "SessionCreate",
    "SessionResponse",
    "SessionListResponse",
    "UserStatsResponse"
]

