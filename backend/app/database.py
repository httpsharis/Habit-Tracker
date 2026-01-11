"""
HabitOS Database Configuration.

Supports SQLite for development and PostgreSQL (Neon) for production.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Get DATABASE_URL from environment, default to SQLite for local dev
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback to SQLite if no DATABASE_URL is set
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'habitos_v2.db')}"
    print("⚠️  No DATABASE_URL found, using SQLite")

# Fix for Neon PostgreSQL - they use 'postgres://' but SQLAlchemy needs 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create SQLAlchemy engine
# SQLite needs check_same_thread=False, PostgreSQL doesn't
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL with connection pooling for better performance
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,        # Increased from 5 to 10
        max_overflow=20,     # Increased from 10 to 20
        pool_pre_ping=True,  # Verify connections are alive
        pool_recycle=300,    # Recycle connections every 5 minutes
        connect_args={
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_db():
    """
    Database session dependency for FastAPI.
    
    Usage:
        @router.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    
    Call this on application startup to ensure all tables exist.
    """
    from app.models import Base as ModelsBase
    ModelsBase.metadata.create_all(bind=engine)
    print(f"✓ Database initialized: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'SQLite'}")
