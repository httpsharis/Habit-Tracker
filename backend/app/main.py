from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, prediction  # Changed predict to prediction

app = FastAPI(title="NeuroHabit API")

# --- CORS SETUP ---
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REGISTER ROUTERS ---
app.include_router(prediction.router, prefix="/api", tags=["Prediction"])  # Changed predict to prediction
app.include_router(chat.router, prefix="/api", tags=["Chat"])

@app.get("/")
def health_check():
    return {"status": "active"}