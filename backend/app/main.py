from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, prediction, user
from app.database import init_db


# ============================================================================
# APPLICATION LIFECYCLE
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    init_db()
    yield


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="HabitOS API",
    description="Personal habit tracking with ML-powered insights and history-based recommendations",
    version="2.0.0",
    lifespan=lifespan
)

# --- CORS SETUP ---
origins = ["http://localhost:3000", "http://127.0.0.1:5500", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REGISTER ROUTERS ---
app.include_router(prediction.router, prefix="/api", tags=["Prediction"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(user.router, prefix="/api", tags=["User"])


@app.get("/")
def health_check():
    return {"status": "active", "service": "HabitOS", "version": "2.0.0"}