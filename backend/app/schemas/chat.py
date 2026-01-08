"""
NeuroHabit Chat Schemas.

Pydantic models for the conversational chat API.
"""
from typing import Optional
from pydantic import BaseModel, Field


class ChatInput(BaseModel):
    """
    Input schema for the /api/talk endpoint.
    
    Attributes:
        user_message: The user's natural language input.
        current_step: Current position in the conversation state machine.
            - 0: Start/Welcome
            - 1: Sleep collection
            - 2: Work intensity collection
            - 3: Stress level collection
            - 4: Mood score collection → triggers prediction
        temp_data: Accumulated user data across conversation steps.
    """
    user_message: str = Field(..., description="User's natural language input")
    current_step: int = Field(..., ge=0, le=4, description="Conversation state (0-4)")
    temp_data: Optional[dict] = Field(default_factory=dict, description="Accumulated biometric data")


class ChatResponse(BaseModel):
    """
    Response schema from the /api/talk endpoint.
    
    Attributes:
        bot_message: NeuroHabit's natural language response.
        next_step: The next state in the conversation flow.
        updated_data: Updated temp_data with any newly collected values.
        prediction: Final prediction object (only present after step 4).
    """
    bot_message: str = Field(..., description="NeuroHabit's response message")
    next_step: int = Field(..., description="Next conversation state")
    updated_data: dict = Field(..., description="Updated temporary data store")
    prediction: Optional[dict] = Field(None, description="ML prediction results")
