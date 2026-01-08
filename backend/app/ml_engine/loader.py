"""
NeuroHabit ML Engine - Model Loader Module.

Provides centralized access to all trained ML models.
"""
from pathlib import Path
from typing import Any
import joblib


# --- PATH CONFIGURATION ---
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "trained_models"


class DummyModel:
    """
    Fallback model for development/testing when real models aren't available.
    Returns neutral predictions that won't break the system.
    """
    def predict(self, X) -> list:
        return [5.0]


def load_model(filename: str) -> Any:
    """
    Load a trained model from disk with graceful fallback.
    
    Args:
        filename: Name of the .pkl file in trained_models/
        
    Returns:
        Loaded sklearn model or DummyModel if file doesn't exist.
    """
    model_path = MODELS_DIR / filename
    if model_path.exists():
        try:
            return joblib.load(model_path)
        except Exception as e:
            print(f"⚠️ Warning: Failed to load {filename}: {e}")
            return DummyModel()
    else:
        print(f"⚠️ Warning: Model {filename} not found at {model_path}. Using dummy.")
        return DummyModel()


# --- SINGLETON MODEL INSTANCES ---
# These are loaded once at module import and reused across requests.

model_regressor = load_model("neuro_predictor_ann.pkl")
"""ANN Regressor: Predicts daily performance score (0-100)."""

model_classifier = load_model("neuro_classifier.pkl")
"""RandomForest Classifier: Predicts day type (0=Recovery, 1=Attack)."""

model_clusterer = load_model("neuro_clusterer.pkl")
"""KMeans Clusterer: Assigns user to a persona cluster."""

model_intent = load_model("intent_model.pkl")
"""NaiveBayes Intent Classifier: Detects user intent from natural language."""


# --- PERSONA MAPPING ---
PERSONA_NAMES = {
    0: "The Night Owl 🦉",
    1: "The Balanced Achiever 🧘",
    2: "The Workaholic 💼"
}
"""Maps cluster IDs to human-readable persona names."""


# --- PUBLIC API ---
__all__ = [
    "model_regressor",
    "model_classifier", 
    "model_clusterer",
    "model_intent",
    "PERSONA_NAMES",
    "load_model",
    "DummyModel"
]
