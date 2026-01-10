"""
HabitOS Database Configuration.

SQLite database connection and session management using SQLAlchemy.
For production, you can switch to PostgreSQL by changing DATABASE_URL.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# SQLite for local development (no installation needed)
# The database file will be created in the backend folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'habitos.db')}"

# For PostgreSQL production, uncomment and configure:
# DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/habitos"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
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
