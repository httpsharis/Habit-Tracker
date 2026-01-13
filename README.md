# 🧠 HabitOS | Intelligent Behavioral Optimization Engine

**HabitOS** is a full-stack, AI-powered behavioral analytics platform designed to bridge the gap between passive habit tracking and active life optimization. Unlike traditional "digital diaries," HabitOS uses a hybrid machine learning architecture to predict daily performance, categorize behavioral archetypes, and provide actionable, sci-fi style directives.

![Project Status](https://img.shields.io/badge/Status-Prototype%20v2.0-blue?style=flat-square)
![Tech Stack](https://img.shields.io/badge/Stack-Next.js%20%7C%20FastAPI%20%7C%20PostgreSQL-green?style=flat-square)

---

## 🚀 Key Features

### 1. **Predictive Analytics Engine (The Brain)**
   - Uses an **Artificial Neural Network (ANN)** to predict a precise "Daily Performance Score" (0-100) based on sleep, work intensity, stress, and mood.
   - Employes **Random Forest Classification** to determine the user's operating mode (e.g., "Attack Mode 🚀" vs. "Recovery Mode 🛡️").

### 2. **Behavioral Clustering (The Sociologist)**
   - Utilizes **K-Means Clustering** to dynamically segment users into personas based on their long-term data (e.g., "The Workaholic," "The Burnout Risk").

### 3. **Explainable AI (White-Box Logic)**
   - Features a **Directive Engine** that doesn't just give a score but explains *why*.
   - Uses logic gates to detect dangerous combinations (e.g., High Stress + Low Sleep) and issues medical-grade protocols (e.g., "NASA Nap," "Box Breathing").

### 4. **Modern "Command Center" UI**
   - Built with **Next.js** and **Tailwind CSS**.
   - Features a glassmorphism design, real-time typing effects, and dynamic score gauges.

---

## 🛠️ Tech Stack

### **Frontend (The Face)**
- **Framework:** Next.js 14 (React)
- **Styling:** Tailwind CSS (Custom "Cyberpunk" Theme)
- **State Management:** React Hooks
- **Deployment:** Vercel

### **Backend (The Logic)**
- **Framework:** FastAPI (Python)
- **ML Libraries:** Scikit-Learn, Pandas, NumPy, Joblib
- **Database:** PostgreSQL (via Neon/Supabase) & SQLAlchemy
- **Deployment:** Render

### **Machine Learning Architecture**
| Model Type | Algorithm | Purpose |
| :--- | :--- | :--- |
| **Regressor** | MLPRegressor (ANN) | Predicts exact performance score (0-100). |
| **Classifier** | Random Forest | Classifies day type (Attack/Recovery). |
| **Clusterer** | K-Means | Identifies user persona/archetype. |
| **NLP** | Naive Bayes | Detects user intent from chat messages. |

---

## 📂 Project Structure

```bash
Habit-Tracker/
├── frontend/             # Next.js Application
│   ├── src/
│   │   ├── components/   # ChatConsole, Background, etc.
│   │   └── app/          # Pages and Global Styles
│   └── package.json
│
├── backend/              # FastAPI Application
│   ├── app/
│   │   ├── main.py       # API Entry Point
│   │   ├── database.py   # PostgreSQL Connection
│   │   ├── routers/      # Chat & History Endpoints
│   │   └── ml_engine/    # Training Scripts
│   ├── models/           # Saved .pkl Brains
│   ├── data/             # Synthetic Training Data
│   └── pyproject.toml    # Python Dependencies
│
└── README.md             # You are here