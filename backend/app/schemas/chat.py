"""
HabitOS Chat Schemas.
"""
from typing import Optional
from pydantic import BaseModel, Field


class ChatInput(BaseModel):
    user_message: str = Field(..., description="User's natural language input")
    current_step: int = Field(..., ge=0, le=6, description="Conversation state (0-6)")
    temp_data: Optional[dict] = Field(default_factory=dict)
    user_id: Optional[int] = Field(None)


class ChatResponse(BaseModel):
    bot_message: str = Field(..., description="HabitOS's response message")
    next_step: int = Field(..., description="Next conversation state")
    updated_data: dict = Field(..., description="Updated temporary data store")
    prediction: Optional[dict] = Field(None, description="ML prediction results")
    acknowledgment: Optional[str] = Field(None, description="Toast message for recorded value")

