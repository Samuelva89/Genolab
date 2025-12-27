import sys
import os

# Add services directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create a file to write our test results
result_file = 'db_test_results.txt'
with open(result_file, 'w') as f:
    f.write('Python path: ' + str(sys.path[0]) + '\n')
    f.write('Current working directory: ' + os.getcwd() + '\n')
    
    # Test importing the config
    try:
        from app.core.config import settings
        f.write('Config imported successfully\n')
        f.write(f'Database URL: {settings.SQLALCHEMY_DATABASE_URL}\n')
    except Exception as e:
        f.write(f'Error importing config: {e}\n')
        import traceback
        f.write(traceback.format_exc() + '\n')

    # Test importing the database
    try:
        from app.database import Base, engine, SessionLocal
        f.write('Database imported successfully\n')
    except Exception as e:
        f.write(f'Error importing database: {e}\n')
        import traceback
        f.write(traceback.format_exc() + '\n')

    # Test importing models
    try:
        from app.models import User
        f.write('Models imported successfully\n')
    except Exception as e:
        f.write(f'Error importing models: {e}\n')
        import traceback
        f.write(traceback.format_exc() + '\n')

    # Test database connection
    try:
        db = SessionLocal()
        f.write('Database session created successfully\n')
        user_count = db.query(User).count()
        f.write(f'User count: {user_count}\n')
        db.close()
        f.write('Database query executed successfully\n')
    except Exception as e:
        f.write(f'Error with database connection: {e}\n')
        import traceback
        f.write(traceback.format_exc() + '\n')

print(f'Test results written to {result_file}')