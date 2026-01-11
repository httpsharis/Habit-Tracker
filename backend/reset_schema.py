"""
Database Reset Script
=====================

Use this script to drop the 'habit_sessions' table.
This is required when the database schema changes (e.g., adding new metrics columns)
and you are using a persistent database (PostgreSQL/Neon) that doesn't update automatically.

Usage:
    poetry run python reset_schema.py
"""
import sys
import os

# Add backend directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.models.session import HabitSession

def reset_schema():
    print("Warning: This will DELETE all habit history data.")
    print(f"Target Database: {engine.url}")
    
    # Auto-confirm for smoother execution
    confirm = 'y'
    print("Auto-confirmed table drop.")

    print("Dropping table 'habit_sessions'...")
    try:
        HabitSession.__table__.drop(bind=engine)
        print("Table dropped successfully.")
        print("Please restart the backend to recreate the table with the correct columns.")
    except Exception as e:
        print(f"Error: {e}")
        print("The table might not exist or there's a connection issue.")
        print("The table might not exist or there's a connection issue.")

if __name__ == "__main__":
    reset_schema()
