import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
print(f'Database URL: {settings.SQLALCHEMY_DATABASE_URL}')

# Check if the database file exists at the expected location
import os.path
db_path = settings.SQLALCHEMY_DATABASE_URL[10:]  # Remove 'sqlite:///'
print(f'Expected database path: {db_path}')
print(f'Database file exists: {os.path.exists(db_path)}')
print(f'Current working directory: {os.getcwd()}')

# Check if we can connect to the database
from app.database import SessionLocal
from app.models import User

db = SessionLocal()
try:
    user_count = db.query(User).count()
    print(f'Number of users in database: {user_count}')
    print('Database connection successful!')
except Exception as e:
    print(f'Database connection failed: {e}')
finally:
    db.close()