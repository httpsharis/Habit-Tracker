"""
Database initialization script.
Run this once to create all tables in Neon.
"""
from dotenv import load_dotenv
load_dotenv()

from app.database import engine, Base, DATABASE_URL
from app.models.user import User
from app.models.session import HabitSession

def init_database():
    """Create all database tables."""
    print(f"Connecting to: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created: users, habit_sessions")

if __name__ == "__main__":
    init_database()