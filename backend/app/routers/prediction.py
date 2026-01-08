"""
NeuroHabit Prediction Router.

Provides a direct prediction API endpoint that bypasses the chat flow.
Useful for programmatic access and testing.
"""
import pandas as pd
from fastapi import APIRouter

from app.schemas import PredictionInput, PredictionResponse
from app.ml_engine import (
    model_regressor,
    model_classifier,
    model_clusterer,
    PERSONA_NAMES
)

router = APIRouter()


def generate_recommendations(data: dict) -> list[str]:
    """Generate strategic directives based on input metrics."""
    tips = []
    
    sleep = data.get('sleep_hours', 8)
    work = data.get('work_intensity', 5)
    stress = data.get('stress_level', 5)
    mood = data.get('mood_score', 5)
    
    if sleep < 6:
        tips.append("CRITICAL: Recovery deficit detected. Circadian realignment protocol recommended.")
    elif sleep > 9:
        tips.append("NOTE: Hypersomnia indicators present. Evaluate sleep quality vs quantity.")
        
    if stress >= 8:
        tips.append("ALERT: Cortisol load elevated. Parasympathetic activation required (Box Breathing, NSDR).")
    
    if work >= 8 and mood < 5:
        tips.append("WARNING: High output/Low affect state. Burnout trajectory detected.")
    
    if mood < 5:
        tips.append("OPTIMIZATION: Dopaminergic baseline low. Recommend sunlight exposure or rewarding micro-tasks.")
    
    if sleep < 7 and work >= 7:
        tips.append("FAILSAFE: Cognitive endurance compromised. Prioritize recovery tonight.")
    
    if not tips:
        tips.append("STATUS: All metrics within optimal bands. Maintain current routine.")
    
    return tips


@router.post("/predict", response_model=PredictionResponse)
def predict_performance(input_data: PredictionInput):
    """
    Direct prediction endpoint.
    
    Bypasses the conversational flow for programmatic access.
    Expects all 4 biometric inputs in a single request.
    """
    features = pd.DataFrame([{
        'sleep_hours': input_data.sleep_hours,
        'work_intensity': input_data.work_intensity,
        'stress_level': input_data.stress_level,
        'mood_score': input_data.mood_score
    }])
    
    pred_score = model_regressor.predict(features)[0]
    pred_class = model_classifier.predict(features)[0]
    pred_cluster = model_clusterer.predict(features)[0]
    
    # Score calculation
    score_sleep = min(input_data.sleep_hours, 9) / 9 * 30
    score_work = input_data.work_intensity / 10 * 20
    score_stress = (10 - input_data.stress_level) / 10 * 20
    score_mood = input_data.mood_score / 10 * 30
    heuristic_score = score_sleep + score_work + score_stress + score_mood
    
    if pred_score != 5.0:
        # Model predicts 0-100 scale. Blend: 70% model, 30% heuristic
        final_score = (pred_score * 0.7) + (heuristic_score * 0.3)
    else:
        final_score = heuristic_score
    
    final_score = min(100, max(0, final_score))
    
    day_type = "🚀 Attack Mode" if pred_class == 1 else "🔋 Recovery Mode"
    persona = PERSONA_NAMES.get(pred_cluster, "Unique Individual 🌟")
    
    recommendations = generate_recommendations({
        'sleep_hours': input_data.sleep_hours,
        'work_intensity': input_data.work_intensity,
        'stress_level': input_data.stress_level,
        'mood_score': input_data.mood_score
    })
    
    return PredictionResponse(
        daily_score=round(final_score, 2),
        day_classification=day_type,
        persona=persona,
        recommendations=recommendations
    )