"""
HabitOS Chat Router.

Implements the conversational state machine for biometric data collection.
Provides natural language interaction with ML-powered predictions and 
history-based personalization.
"""
import re
import random
from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas import ChatInput, ChatResponse
from app.database import get_db
from app.models.user import User
from app.models.session import HabitSession
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
# USER HISTORY HELPERS
# ============================================================================

def get_user_history(db: Session, user_id: int, days: int = 7) -> List[HabitSession]:
    """Get user's recent sessions for trend analysis."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    return db.query(HabitSession)\
        .filter(HabitSession.user_id == user_id)\
        .filter(HabitSession.created_at >= cutoff_date)\
        .order_by(HabitSession.created_at.desc())\
        .all()


def calculate_averages(sessions: List[HabitSession]) -> dict:
    """Calculate average metrics from sessions."""
    if not sessions:
        return {}
    
    total = len(sessions)
    return {
        'avg_sleep': round(sum(s.sleep_hours for s in sessions) / total, 1),
        'avg_work': round(sum(s.work_intensity for s in sessions) / total, 1),
        'avg_stress': round(sum(s.stress_level for s in sessions) / total, 1),
        'avg_mood': round(sum(s.mood_score for s in sessions) / total, 1),
        'avg_screen': round(sum(s.screen_time or 0 for s in sessions) / total, 1),
        'avg_hydration': round(sum(s.hydration or 0 for s in sessions) / total, 1),
        'avg_score': round(sum(s.daily_score for s in sessions) / total, 1),
        'session_count': total
    }


def get_trend_indicator(current: float, average: float, lower_is_better: bool = False) -> str:
    """Get trend arrow based on comparison to average."""
    if average == 0:
        return ""
    
    diff_percent = ((current - average) / average) * 100
    
    if lower_is_better:
        if diff_percent < -10:
            return "↓ better than your average"
        elif diff_percent > 10:
            return "↑ higher than your average"
    else:
        if diff_percent > 10:
            return "↑ above your average"
        elif diff_percent < -10:
            return "↓ below your average"
    
    return "↔ consistent"


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
        ],
        'screen': [
            f"Screen time logged: {value} hours.",
            f"Digital exposure recorded: {value}h.",
            f"Display time tracked: {value} hours."
        ],
        'hydration': [
            f"Hydration level: {value} glasses.",
            f"Water intake recorded: {value}.",
            f"Fluid consumption logged: {value} glasses."
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
            "How's your mood? (1-10)",
            "Rate your psychological state (1-10).",
            "Mood score for today (1-10)?"
        ],
        5: [
            "How many hours of screen time today?",
            "Digital exposure - hours on screens?",
            "Screen time in hours (0-24)?"
        ],
        6: [
            "Final metric: Glasses of water/hydration today?",
            "Last one - how many glasses of water?",
            "Hydration check: glasses consumed today (0-20)?"
        ]
    }
    
    return random.choice(prompts.get(step, ["Please provide the next value."]))


def generate_recommendations(data: dict, history: Optional[dict] = None) -> list[str]:
    """
    Generate actionable insights based on collected biometrics and history.
    
    Focuses on practical, conversational advice rather than clinical alerts.
    """
    tips = []
    
    sleep = data.get('sleep_hours', 8)
    work = data.get('work_intensity', 5)
    stress = data.get('stress_level', 5)
    mood = data.get('mood_score', 5)
    screen = data.get('screen_time', 0)
    hydration = data.get('hydration', 0)
    
    # --- Sleep insights ---
    if sleep < 5:
        tips.append("You're running on fumes. Try to get to bed 30 minutes earlier tonight.")
    elif sleep < 6:
        tips.append("A bit short on sleep—consider a 20-minute power nap if you can.")
    elif sleep > 9:
        tips.append("Sleeping over 9 hours can sometimes mean poor sleep quality. How do you feel?")
    
    # --- Stress insights ---
    if stress >= 8:
        tips.append("Stress is high today. A quick walk or some deep breaths can help reset.")
        if history and history.get('avg_stress', 0) >= 7:
            tips.append("You've been stressed for a few days now. Worth checking what's driving it.")
    elif stress >= 6:
        tips.append("Moderate stress detected. Take short breaks to stay sharp.")
    
    # --- Burnout warning ---
    if work >= 8 and mood < 5:
        tips.append("Pushing hard but feeling low? That's a sign to step back and recharge.")
    
    # --- Mood support ---
    if mood <= 3:
        tips.append("Tough day? Even 10 minutes outside or a chat with someone can help.")
    elif mood < 5:
        tips.append("Mood's a bit low. Small wins and fresh air work wonders.")
        if history and history.get('avg_mood', 10) >= 7:
            tips.append("This is lower than your usual. Something on your mind?")
    
    # --- Sleep + high workload ---
    if sleep < 7 and work >= 7:
        tips.append("Low sleep plus high output isn't sustainable. Prioritize rest tonight.")
    
    # --- Screen time ---
    if screen > 10:
        tips.append("That's a lot of screen time. Give your eyes a break every 30 minutes.")
    elif screen > 6:
        tips.append("Screen time is adding up. Try the 20-20-20 rule: every 20 min, look 20 feet away for 20 sec.")
    
    # --- Hydration ---
    if hydration < 3:
        tips.append("You're quite dehydrated. Keep a water bottle nearby as a reminder.")
    elif hydration < 5:
        tips.append("Could use more water. Aim for 8 glasses throughout the day.")
    elif hydration >= 8:
        tips.append("Great hydration today!")
    
    # --- Positive patterns from history ---
    if history and history.get('session_count', 0) >= 3:
        avg_score = history.get('avg_score', 50)
        if avg_score >= 75:
            tips.append(f"You've been consistent lately—7-day average is {avg_score:.0f}/100. Keep it up!")
        elif avg_score >= 60:
            tips.append("Solid week so far. Small improvements add up.")
    
    # --- Positive reinforcement ---
    if sleep >= 7 and stress <= 4 and mood >= 7:
        tips.append("You're in a good spot today. Make the most of it!")
    
    # Default when everything looks fine
    if not tips:
        tips.append("Looking balanced today. Keep doing what you're doing.")
    
    return tips


def generate_trend_analysis(data: dict, history: dict) -> str:
    """Generate trend analysis section for the report."""
    if not history or history.get('session_count', 0) == 0:
        return ""
    
    lines = ["\n📈 TREND ANALYSIS (vs 7-day avg):"]
    
    # Sleep trend
    sleep_trend = get_trend_indicator(data.get('sleep_hours', 0), history.get('avg_sleep', 0))
    if sleep_trend:
        lines.append(f"   • Sleep: {data.get('sleep_hours', 0)}h {sleep_trend}")
    
    # Stress trend (lower is better)
    stress_trend = get_trend_indicator(data.get('stress_level', 0), history.get('avg_stress', 0), lower_is_better=True)
    if stress_trend:
        lines.append(f"   • Stress: {data.get('stress_level', 0)}/10 {stress_trend}")
    
    # Mood trend
    mood_trend = get_trend_indicator(data.get('mood_score', 0), history.get('avg_mood', 0))
    if mood_trend:
        lines.append(f"   • Mood: {data.get('mood_score', 0)}/10 {mood_trend}")
    
    lines.append(f"   • Sessions this week: {history.get('session_count', 0)}")
    
    return "\n".join(lines)


def save_session_to_db(db: Session, user_id: int, data: dict, prediction: dict):
    """Save completed session to database."""
    try:
        session = HabitSession(
            user_id=user_id,
            sleep_hours=data.get('sleep_hours', 0),
            work_intensity=data.get('work_intensity', 0),
            stress_level=data.get('stress_level', 0),
            mood_score=data.get('mood_score', 0),
            screen_time=data.get('screen_time', 0),
            hydration=data.get('hydration', 0),
            daily_score=prediction.get('daily_score', 0),
            day_classification=prediction.get('day_classification', 'Unknown'),
            persona=prediction.get('persona', 'Unknown')
        )
        db.add(session)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error saving session: {e}")


# ============================================================================
# MAIN CHAT ENDPOINT
# ============================================================================

@router.post("/talk", response_model=ChatResponse)
def chat_with_ai(input_data: ChatInput, db: Session = Depends(get_db)):
    """
    Main conversational endpoint implementing a 7-step state machine.
    
    State Flow:
        0: Start → Welcome message
        1: Collect sleep_hours
        2: Collect work_intensity
        3: Collect stress_level
        4: Collect mood_score
        5: Collect screen_time
        6: Collect hydration → Trigger prediction
        
    Returns to state 0 after prediction for a new session.
    
    If user_id is provided, session is saved to database and
    responses are personalized based on history.
    """
    step = input_data.current_step
    message = input_data.user_message.lower().strip()
    data = input_data.temp_data or {}
    user_id = input_data.user_id

    bot_msg = ""
    next_step = step
    prediction = None
    
    # Get user history if user_id provided
    history = None
    if user_id:
        user_sessions = get_user_history(db, user_id)
        history = calculate_averages(user_sessions)
    
    # --- Extract number from input ---
    number_val = extract_number(message)
    
    # --- Intent Detection (only for non-numeric inputs) ---
    # intent = None
    # if number_val is None or len(message.split()) > 3:
    #     try:
    #         intent = model_intent.predict([message])[0]
    #     except:
    #         pass

    # if intent:
    #     intent_map = {'greeting': 0, 'sleep': 1, 'work': 2, 'stress': 3, 'mood': 4}
    #     if intent in intent_map:
    #         mapped_step = intent_map[intent]
    #         if mapped_step != step:
    #             step = mapped_step

    # --- Handle "Go Back" Command ---
    if check_go_back(message) and step > 0:
        if step == 1:
            next_step = 0
            bot_msg = "Session reset. Reinitializing...\n\n" + _get_welcome_message()
        else:
            step_data_keys = {
                2: 'sleep_hours', 3: 'work_intensity', 4: 'stress_level',
                5: 'mood_score', 6: 'screen_time'
            }
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
                bot_message="How many hours did you sleep?",
                next_step=1,
                updated_data=data
            )
        if number_val < 0 or number_val > 24:
            return ChatResponse(
                bot_message="Please enter hours between 0-24.",
                next_step=1,
                updated_data=data
            )
        data['sleep_hours'] = number_val
        bot_msg = get_prompt(2)  # Just the next question
        next_step = 2
        
        return ChatResponse(
            bot_message=bot_msg,
            next_step=next_step,
            updated_data=data,
            acknowledgment=f"✓ {number_val} hours logged"  # Separate acknowledgment
        )

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
        bot_msg = f"{get_acknowledgment('mood', val)}\n\n{get_prompt(5)}"
        next_step = 5

    elif step == 5:
        if number_val is None:
            return ChatResponse(
                bot_message="I need a number (0-24) for screen time hours.",
                next_step=5,
                updated_data=data
            )
        val = max(0, min(24, number_val))
        data['screen_time'] = val
        bot_msg = f"{get_acknowledgment('screen', val)}\n\n{get_prompt(6)}"
        next_step = 6

    elif step == 6:
        if number_val is None:
            return ChatResponse(
                bot_message="I need a number (0-20) for glasses of water.",
                next_step=6,
                updated_data=data
            )
        val = max(0, min(20, number_val))
        data['hydration'] = val

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

        # --- Calculate Score with Better Logic ---
        
        # Sleep: 7-9 hours is optimal (25 points max)
        sleep = data.get('sleep_hours', 0)
        if 7 <= sleep <= 9:
            score_sleep = 25  # Perfect sleep
        elif 6 <= sleep < 7 or 9 < sleep <= 10:
            score_sleep = 20  # Good sleep
        elif 5 <= sleep < 6:
            score_sleep = 12  # Okay
        else:
            score_sleep = max(0, sleep / 9 * 15)  # Poor
        
        # Work: Moderate is best (not too lazy, not burnout) - 15 points max
        work = data.get('work_intensity', 5)
        if 4 <= work <= 7:
            score_work = 15  # Balanced workday
        elif 3 <= work < 4 or 7 < work <= 8:
            score_work = 12
        else:
            score_work = 8  # Either too lazy or burning out
        
        # Stress: Lower is better - 20 points max
        stress = data.get('stress_level', 5)
        score_stress = max(0, (10 - stress) / 10 * 20)
        
        # Mood: Higher is better - 20 points max
        mood = data.get('mood_score', 5)
        score_mood = mood / 10 * 20
        
        # Screen time: Less is better, under 4 hours is great - 10 points max
        screen = data.get('screen_time', 0)
        if screen <= 3:
            score_screen = 10
        elif screen <= 6:
            score_screen = 7
        elif screen <= 10:
            score_screen = 4
        else:
            score_screen = 1
        
        # Hydration: 8+ glasses is perfect - 10 points max
        hydration = data.get('hydration', 0)
        score_hydration = min(hydration, 8) / 8 * 10
        
        heuristic_score = score_sleep + score_work + score_stress + score_mood + score_screen + score_hydration
        
        # Use heuristic score primarily, ML as secondary influence
        if pred_score != 5.0:
            # ML model has a real prediction - blend 30% ML, 70% heuristic
            final_score = (pred_score * 0.3) + (heuristic_score * 0.7)
        else:
            # ML model returned default - use pure heuristic
            final_score = heuristic_score
        
        final_score = min(100, max(0, final_score))

        day_type = "🚀 Attack Mode" if pred_class == 1 else "🔋 Recovery Mode"
        day_explanation = "You're primed for deep work today." if pred_class == 1 else "Focus on rest and recovery."
        persona = PERSONA_NAMES.get(pred_cluster, "Unique Individual 🌟")
        
        # Generate history-aware recommendations
        recommendations = generate_recommendations(data, history)
        recs_text = "\n".join([f"  • {rec}" for rec in recommendations])
        
        # Generate trend analysis
        trend_text = generate_trend_analysis(data, history) if history else ""
        
        # Score comparison to history
        score_comparison = ""
        if history and history.get('avg_score'):
            diff = final_score - history['avg_score']
            if diff > 0:
                score_comparison = f"   ↑ {diff:.1f} points above your 7-day average"
            elif diff < 0:
                score_comparison = f"   ↓ {abs(diff):.1f} points below your 7-day average"
            else:
                score_comparison = "   ↔ Consistent with your average"
        
        bot_msg = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  HABITOS PERFORMANCE REPORT\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 PERFORMANCE INDEX: {final_score:.1f}/100\n"
            f"{score_comparison}\n\n"
            f"⚡ CLASSIFICATION: {day_type}\n"
            f"   {day_explanation}\n\n"
            f"🧬 PERSONA: {persona}\n"
            f"{trend_text}\n\n"
            f"📋 PERSONALIZED DIRECTIVES:\n{recs_text}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Session complete. Say 'start' for new analysis."
        )

        prediction = {
            "daily_score": round(final_score, 2),
            "day_classification": day_type,
            "persona": persona,
            "recommendations": recommendations
        }

        # Save session to database if user_id provided
        if user_id:
            save_session_to_db(db, user_id, data, prediction)

        next_step = 0
        data = {}

    return ChatResponse(
        bot_message=bot_msg,
        next_step=next_step,
        updated_data=data,
        prediction=prediction,
        acknowledgment=bot_msg  # Include acknowledgment in the response
    )


def _get_welcome_message() -> str:
    """Generate the welcome/initialization message."""
    return "Ready for your daily check-in. Let's start with sleep."
