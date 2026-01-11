"""
Quick database inspection script.
Shows all users and their session counts.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import text

def inspect_db():
    print("=== Database Inspection ===\n")
    
    with engine.connect() as conn:
        # Check users
        print("Users:")
        result = conn.execute(text("SELECT id, username FROM users"))
        users = result.fetchall()
        if not users:
            print("  (No users found)")
        for u in users:
            print(f"  - ID: {u[0]}, Username: {u[1]}")
        
        print("\nSessions per user:")
        result = conn.execute(text("""
            SELECT user_id, COUNT(*) as count 
            FROM habit_sessions 
            GROUP BY user_id
        """))
        sessions = result.fetchall()
        if not sessions:
            print("  (No sessions found)")
        for s in sessions:
            print(f"  - User ID {s[0]}: {s[1]} sessions")
        
        print("\nTotal sessions:")
        result = conn.execute(text("SELECT COUNT(*) FROM habit_sessions"))
        total = result.fetchone()[0]
        print(f"  {total} total sessions in database")

if __name__ == "__main__":
    inspect_db()
