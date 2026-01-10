"""
NeuroHabit Biometric Model Trainer.

Trains all core ML models for the prediction engine:
- ANN Regressor (Performance Score)
- RandomForest Classifier (Day Type)
- KMeans Clusterer (Persona Detection)
"""
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, accuracy_score
from pathlib import Path

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "neurohabit_synthetic_data.csv"
MODEL_SAVE_PATH = BASE_DIR / "trained_models"


def generate_synthetic_data(n_samples: int = 1000) -> pd.DataFrame:
    """Generate synthetic training data if real data doesn't exist."""
    np.random.seed(42)
    
    data = {
        'sleep_hours': np.clip(np.random.normal(7, 1.5, n_samples), 3, 10),
        'work_intensity': np.clip(np.random.normal(5.5, 2, n_samples), 1, 10),
        'stress_level': np.clip(np.random.normal(5, 2, n_samples), 1, 10),
        'mood_score': np.clip(np.random.normal(6, 2, n_samples), 1, 10),
    }
    
    df = pd.DataFrame(data)
    
    # Heuristic scoring with realistic variance
    df['daily_performance_score'] = (
        (df['sleep_hours'] / 9 * 30) + 
        (df['work_intensity'] / 10 * 20) + 
        ((10 - df['stress_level']) / 10 * 20) + 
        (df['mood_score'] / 10 * 30)
    ) * (1 + np.random.normal(0, 0.08, n_samples))
    
    df['daily_performance_score'] = df['daily_performance_score'].clip(0, 100)
     
    return df


def train_models():
    """Train and save all ML models."""
    print("=" * 50)
    print("    NEUROHABIT MODEL TRAINING SUITE")
    print("=" * 50)
    
    # Ensure directories exist
    MODEL_SAVE_PATH.mkdir(parents=True, exist_ok=True)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Load or generate data
    if DATA_PATH.exists():
        df = pd.read_csv(DATA_PATH)
        print(f"\n📁 Data loaded from {DATA_PATH}")
    else:
        print(f"\n⚠️  Data file not found. Generating synthetic data...")
        df = generate_synthetic_data()
        df.to_csv(DATA_PATH, index=False)
        print(f"   Saved to {DATA_PATH}")
    
    print(f"   Shape: {df.shape}")
    
    # Features and targets
    features = ['sleep_hours', 'work_intensity', 'stress_level', 'mood_score']
    X = df[features]
    y_score = df['daily_performance_score']
    
    # --- MODEL 1: ANN Regressor ---
    print("\n🧠 Training Model 1: Predictor (ANN)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_score, test_size=0.2, random_state=42
    )
    
    model_regressor = MLPRegressor(
        hidden_layer_sizes=(64, 32),
        max_iter=500,
        random_state=42,
        early_stopping=True
    )
    model_regressor.fit(X_train, y_train)
    
    predictions = model_regressor.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    print(f"   → MAE: {mae:.2f} points")
    
    # --- MODEL 2: RandomForest Classifier ---
    print("\n🛡️  Training Model 2: Classifier (RandomForest)...")
    y_class = (df['daily_performance_score'] > 60).astype(int)
    
    rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_classifier.fit(X, y_class)
    
    acc = accuracy_score(y_class, rf_classifier.predict(X))
    print(f"   → Training Accuracy: {acc*100:.1f}%")
    
    # --- MODEL 3: KMeans Clusterer ---
    print("\n🧩 Training Model 3: Clusterer (KMeans)...")
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(X)
    
    df['cluster'] = kmeans.labels_
    print("   → Cluster profiles:")
    cluster_stats = df.groupby('cluster')[['sleep_hours', 'daily_performance_score']].mean()
    for idx, row in cluster_stats.iterrows():
        print(f"      Cluster {idx}: Sleep={row['sleep_hours']:.1f}h, Score={row['daily_performance_score']:.1f}")
    
    # --- SAVE MODELS ---
    print("\n💾 Saving models...")
    joblib.dump(model_regressor, MODEL_SAVE_PATH / "neuro_predictor_ann.pkl")
    joblib.dump(rf_classifier, MODEL_SAVE_PATH / "neuro_classifier.pkl")
    joblib.dump(kmeans, MODEL_SAVE_PATH / "neuro_clusterer.pkl")
    
    print(f"\n✅ DONE! Models saved to {MODEL_SAVE_PATH}")
    print("=" * 50)


if __name__ == "__main__":
    train_models()
