"""
NeuroHabit Intent Model Trainer.

Trains a Naive Bayes classifier for intent detection in conversational inputs.
"""
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib
from pathlib import Path

# Training data: (text, intent)
TRAINING_DATA = [
    # Sleep intents
    ("I slept 8 hours", "sleep"),
    ("slept for 5 hours", "sleep"),
    ("had 7 hours of sleep", "sleep"),
    ("my sleep was bad, only 4 hours", "sleep"),
    ("I slept amazing", "sleep"),
    ("sleep", "sleep"),
    ("didn't sleep well", "sleep"),
    ("got 6 hours rest", "sleep"),
    
    # Work intents
    ("work was intense", "work"),
    ("very hard day at work", "work"),
    ("I studied for 10 hours", "work"),
    ("My productivity was high", "work"),
    ("work", "work"),
    ("intensity 8", "work"),
    ("busy day", "work"),
    ("worked overtime", "work"),

    # Stress intents
    ("stress is high", "stress"),
    ("I am very stressed", "stress"),
    ("feeling anxious", "stress"),
    ("stress level 9", "stress"),
    ("no stress today", "stress"),
    ("relaxed", "stress"),
    ("overwhelmed", "stress"),
    ("calm and collected", "stress"),

    # Mood intents
    ("mood is good", "mood"),
    ("I feel great", "mood"),
    ("feeling sad", "mood"),
    ("mood 5", "mood"),
    ("happy", "mood"),
    ("awful day", "mood"),
    ("feeling down", "mood"),
    ("energetic", "mood"),

    # Greeting/Start intents
    ("hi", "greeting"),
    ("hello", "greeting"),
    ("hey", "greeting"),
    ("start", "greeting"),
    ("begin", "greeting"),
    ("let's go", "greeting"),
    
    # Exit intents
    ("bye", "exit"),
    ("exit", "exit"),
    ("quit", "exit"),
    ("goodbye", "exit")
]


def train_intent_model():
    """Train and save the intent classification model."""
    df = pd.DataFrame(TRAINING_DATA, columns=['text', 'intent'])
    
    model = make_pipeline(CountVectorizer(), MultinomialNB())
    model.fit(df['text'], df['intent'])
    
    # Save model
    save_path = Path(__file__).resolve().parent / "trained_models" / "intent_model.pkl"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, save_path)
    
    print(f"✅ Intent model trained and saved to {save_path}")
    print(f"   Training samples: {len(df)}")
    print(f"   Intents: {df['intent'].unique().tolist()}")


if __name__ == "__main__":
    train_intent_model()
