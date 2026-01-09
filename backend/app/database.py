"""
HabitOS Database Configuration.

PostgreSQL database connection and session management using SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# PostgreSQL connection URL
# Format: postgresql://username:password@host:port/database
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/habitos"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_size=5,         # Connection pool size
    max_overflow=10      # Max additional connections
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
