"""
NeuroHabit Chat Router.

Implements the conversational state machine for biometric data collection.
Provides natural language interaction with ML-powered predictions.
"""
import re
import random
import pandas as pd
from fastapi import APIRouter

from app.schemas import ChatInput, ChatResponse
from app.ml_engine import (
    model_regressor,
    model_classifier,
    model_clusterer,
    model_intent,
    PERSONA_NAMES
)

router = APIRouter()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def extract_number(text: str) -> float | None:
    """
    Extract the first number from natural language text.
    
    Examples:
        "I slept 7 hours" -> 7.0
        "about 8.5" -> 8.5
        "seven" -> None (word numbers not supported yet)
    """
    matches = re.findall(r"[-+]?\d*\.?\d+", text)
    return float(matches[0]) if matches else None


def check_go_back(message: str) -> bool:
    """Check if user wants to navigate backwards in the conversation."""
    back_keywords = ['back', 'undo', 'previous', 'go back', 'restart', 'start over']
    return any(keyword in message.lower() for keyword in back_keywords)


# ============================================================================
# NATURAL LANGUAGE GENERATION (NLG)
# ============================================================================

def get_acknowledgment(metric: str, value: float) -> str:
    """Generate varied acknowledgment responses for collected data."""
    
    templates = {
        'sleep': [
            f"Logged {value} hours of recovery time.",
            f"Sleep data captured: {value}h.",
            f"Recovery metric recorded: {value} hours."
        ],
        'work': [
            f"Strain level {value}/10 recorded.",
            f"Work intensity captured: {value}/10.",
            f"Cognitive load registered at {value}."
        ],
        'stress': [
            f"Stress parameter: {value}/10.",
            f"Load factor recorded: {value}.",
            f"Anxiety index logged: {value}/10."
        ],
        'mood': [
            f"Psychological state: {value}/10.",
            f"Affect score captured: {value}.",
            f"Mood baseline: {value}/10."
        ]
    }
    
    return random.choice(templates.get(metric, [f"Value {value} recorded."]))


def get_prompt(step: int) -> str:
    """Generate the next question prompt with slight variation."""
    
    prompts = {
        1: [
            "How many hours did you sleep last night?",
            "Let's start with recovery. Sleep duration in hours?",
            "First metric: How much sleep did you get?"
        ],
        2: [
            "Rate your work/study intensity today (1-10).",
            "How demanding was your cognitive load today? (1-10)",
            "On a scale of 1-10, how intense was your output?"
        ],
        3: [
            "What's your stress level right now? (1-10)",
            "Rate your current stress on a 1-10 scale.",
            "Quantify your stress load (1-10)."
        ],
        4: [
            "Final metric: How's your mood? (1-10)",
            "Last one - rate your psychological state (1-10).",
            "Mood score to complete the analysis (1-10)?"
        ]
    }
    
    return random.choice(prompts.get(step, ["Please provide the next value."]))


def generate_recommendations(data: dict) -> list[str]:
    """Generate strategic directives based on collected biometrics."""
    tips = []
    
    sleep = data.get('sleep_hours', 8)
    work = data.get('work_intensity', 5)
    stress = data.get('stress_level', 5)
    mood = data.get('mood_score', 5)
    
    if sleep < 6:
        tips.append("CRITICAL: Recovery deficit. Circadian realignment protocol: Bedtime -30min tonight.")
    elif sleep > 9:
        tips.append("NOTE: Hypersomnia detected. Evaluate sleep quality vs quantity.")
        
    if stress >= 8:
        tips.append("ALERT: Cortisol overload. Execute parasympathetic reset (Box Breathing x4, or 10min NSDR).")
    
    if work >= 8 and mood < 5:
        tips.append("WARNING: High output + Low affect = Burnout vector. Mandatory disconnect window required.")
    
    if mood < 5:
        tips.append("OPTIMIZE: Dopamine baseline low. Prescribe: Sunlight exposure, micro-wins, or movement.")
    
    if sleep < 7 and work >= 7:
        tips.append("FAILSAFE: Cognitive battery depleted. Tonight's recovery is non-negotiable.")
    
    if not tips:
        tips.append("STATUS: All systems nominal. Maintain current operating parameters.")
    
    return tips


# ============================================================================
# MAIN CHAT ENDPOINT
# ============================================================================

@router.post("/talk", response_model=ChatResponse)
def chat_with_ai(input_data: ChatInput):
    """
    Main conversational endpoint implementing a 5-step state machine.
    
    State Flow:
        0: Start → Welcome message
        1: Collect sleep_hours
        2: Collect work_intensity
        3: Collect stress_level
        4: Collect mood_score → Trigger prediction
        
    Returns to state 0 after prediction for a new session.
    """
    step = input_data.current_step
    message = input_data.user_message.lower().strip()
    data = input_data.temp_data or {}

    bot_msg = ""
    next_step = step
    prediction = None
    
    # --- Extract number from input ---
    number_val = extract_number(message)
    
    # --- Intent Detection (only for non-numeric inputs) ---
    intent = None
    if number_val is None or len(message.split()) > 3:
        try:
            intent = model_intent.predict([message])[0]
        except:
            pass

    if intent:
        intent_map = {'greeting': 0, 'sleep': 1, 'work': 2, 'stress': 3, 'mood': 4}
        if intent in intent_map:
            mapped_step = intent_map[intent]
            if mapped_step != step:
                step = mapped_step

    # --- Handle "Go Back" Command ---
    if check_go_back(message) and step > 0:
        if step == 1:
            next_step = 0
            bot_msg = "Session reset. Reinitializing...\n\n" + _get_welcome_message()
        else:
            step_data_keys = {2: 'sleep_hours', 3: 'work_intensity', 4: 'stress_level'}
            if step in step_data_keys:
                data.pop(step_data_keys[step], None)
            next_step = step - 1
            bot_msg = f"Returning to previous metric.\n\n{get_prompt(next_step)}"
        
        return ChatResponse(bot_message=bot_msg, next_step=next_step, updated_data=data)

    # --- Main Conversation Flow ---
    if step == 0:
        bot_msg = _get_welcome_message()
        next_step = 1

    elif step == 1:
        if number_val is None:
            return ChatResponse(
                bot_message="I need a numeric value. How many hours did you sleep?",
                next_step=1,
                updated_data=data
            )
        if number_val < 0 or number_val > 24:
            return ChatResponse(
                bot_message="Invalid range. Please enter hours between 0-24.",
                next_step=1,
                updated_data=data
            )
        data['sleep_hours'] = number_val
        bot_msg = f"{get_acknowledgment('sleep', number_val)}\n\n{get_prompt(2)}"
        next_step = 2

    elif step == 2:
        if number_val is None:
            return ChatResponse(
                bot_message="I need a number (1-10) for work intensity.",
                next_step=2,
                updated_data=data
            )
        val = max(1, min(10, number_val))
        data['work_intensity'] = val
        bot_msg = f"{get_acknowledgment('work', val)}\n\n{get_prompt(3)}"
        next_step = 3

    elif step == 3:
        if number_val is None:
            return ChatResponse(
                bot_message="I need a number (1-10) for stress level.",
                next_step=3,
                updated_data=data
            )
        val = max(1, min(10, number_val))
        data['stress_level'] = val
        bot_msg = f"{get_acknowledgment('stress', val)}\n\n{get_prompt(4)}"
        next_step = 4

    elif step == 4:
        if number_val is None:
            return ChatResponse(
                bot_message="I need a number (1-10) for mood.",
                next_step=4,
                updated_data=data
            )
        val = max(1, min(10, number_val))
        data['mood_score'] = val

        # --- Run ML Predictions ---
        features = pd.DataFrame([{
            'sleep_hours': data.get('sleep_hours', 7.0),
            'work_intensity': data.get('work_intensity', 5.0),
            'stress_level': data.get('stress_level', 5.0),
            'mood_score': data.get('mood_score', 5.0)
        }])

        pred_score = model_regressor.predict(features)[0]
        pred_class = model_classifier.predict(features)[0]
        pred_cluster = model_clusterer.predict(features)[0]

        # Calculate final score
        # Heuristic: weighted sum of normalized inputs (0-100 scale)
        score_sleep = min(data.get('sleep_hours', 0), 9) / 9 * 30
        score_work = data.get('work_intensity', 0) / 10 * 20
        score_stress = (10 - data.get('stress_level', 0)) / 10 * 20
        score_mood = data.get('mood_score', 0) / 10 * 30
        heuristic_score = score_sleep + score_work + score_stress + score_mood
        
        # Model predicts on 0-100 scale. Blend with heuristic if model is valid.
        if pred_score != 5.0:
            # 70% model, 30% heuristic
            final_score = (pred_score * 0.7) + (heuristic_score * 0.3)
        else:
            final_score = heuristic_score
        final_score = min(100, max(0, final_score))

        day_type = "🚀 Attack Mode" if pred_class == 1 else "🔋 Recovery Mode"
        persona = PERSONA_NAMES.get(pred_cluster, "Unique Individual 🌟")
        recommendations = generate_recommendations(data)
        
        recs_text = "\n".join([f"  • {rec}" for rec in recommendations])
        
        bot_msg = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  NEUROHABIT PERFORMANCE REPORT\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 PERFORMANCE INDEX: {final_score:.1f}/100\n"
            f"⚡ CLASSIFICATION: {day_type}\n"
            f"🧬 PERSONA: {persona}\n\n"
            f"📋 STRATEGIC DIRECTIVES:\n{recs_text}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Session complete. Say 'start' for new analysis."
        )

        prediction = {
            "daily_score": round(final_score, 2),
            "day_classification": day_type,
            "persona": persona,
            "recommendations": recommendations
        }

        next_step = 0
        data = {}

    return ChatResponse(
        bot_message=bot_msg,
        next_step=next_step,
        updated_data=data,
        prediction=prediction
    )


def _get_welcome_message() -> str:
    """Generate the welcome/initialization message."""
    return (
        "**NeuroHabit Core** initialized.\n"
        "Biometric analysis system ready.\n\n"
        "I'll collect 4 metrics to generate your performance forecast:\n"
        "  1. Recovery (Sleep Duration)\n"
        "  2. Strain (Work Intensity)\n"
        "  3. Load (Stress Level)\n"
        "  4. State (Mood Score)\n\n"
        f"{get_prompt(1)}"
    )
