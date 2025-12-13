"""
Initialization script for MySQL database in Genolab application.
This script handles the database setup and initial data population.
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, ProgrammingError

# Add the services directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/services')

from app.core.config import settings
from app.database import Base
from app.models import User, Organism, Strain, Analysis
from app import crud
from app.schemas import UserCreate

def initialize_mysql_database():
    """Initialize MySQL database with proper configuration"""
    
    # Create the engine using the database URL from settings
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
    
    print("Initializing MySQL database...")
    
    try:
        # Connect to the database
        with engine.connect() as conn:
            # Test the connection
            result = conn.execute(text("SELECT 1"))
            print("Database connection successful!")
            
            # Create tables using SQLAlchemy
            print("Creating tables...")
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully!")
            
    except OperationalError as e:
        print(f"Operational Error connecting to database: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error initializing database: {e}")
        return False
    
    # Create default user if not exists
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("Checking for existing users...")
        existing_user = db.query(User).first()
        
        if not existing_user:
            print("Creating default user...")
            default_user = UserCreate(
                email="admin@genolab.edu",
                name="Admin User",
                is_admin=True
            )
            
            # Assuming you have a method to create user in your CRUD module
            created_user = crud.create_user(db=db, user=default_user)
            db.commit()
            print(f"Default user created: {created_user.email}")
        else:
            print(f"User already exists: {existing_user.email}")
            
        db.close()
        print("Database initialization completed!")
        return True
        
    except Exception as e:
        print(f"Error creating default user: {e}")
        return False

if __name__ == "__main__":
    if initialize_mysql_database():
        print("MySQL database initialization completed successfully!")
    else:
        print("MySQL database initialization failed!")
        sys.exit(1)