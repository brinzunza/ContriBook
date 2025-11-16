"""
Migration script to add blockchain_db_path column to teams table.
Run this script once to update your database schema.
"""
import sys
from sqlalchemy import text
from app.database import engine, SessionLocal
from app.config import settings

def migrate():
    """Add blockchain_db_path column to teams table if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if column exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='teams' AND column_name='blockchain_db_path'
        """))
        
        if result.fetchone():
            print("Column 'blockchain_db_path' already exists. Migration not needed.")
            return
        
        # Add the column
        print("Adding 'blockchain_db_path' column to 'teams' table...")
        db.execute(text("""
            ALTER TABLE teams 
            ADD COLUMN blockchain_db_path VARCHAR UNIQUE
        """))
        db.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Migration failed: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print(f"Connecting to database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'local'}")
    migrate()

