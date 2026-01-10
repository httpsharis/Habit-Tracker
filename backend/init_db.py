"""
Database initialization script.
Run this once to create all tables.
"""
from app.database import engine, Base
from app.models.user import User
from app.models.session import HabitSession

def init_database():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized successfully!")
    print(f"✓ Tables created: users, habit_sessions")

if __name__ == "__main__":
    init_database()