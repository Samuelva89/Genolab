import sys
import os

# Add services directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create a file to write our test results
result_file = 'stats_test_results.txt'
with open(result_file, 'w') as f:
    f.write('Testing stats functions...\n')
    
    try:
        from app.core.config import settings
        f.write(f'Database URL: {settings.SQLALCHEMY_DATABASE_URL}\n')
        
        # Test the database functions directly
        from app.database import SessionLocal
        from app import crud
        
        db = SessionLocal()
        try:
            total_organisms = crud.get_organisms_count(db)
            total_strains = crud.get_strains_count(db)
            total_analyses = crud.get_analyses_count(db)
            
            f.write(f'Total organisms: {total_organisms}\n')
            f.write(f'Total strains: {total_strains}\n')
            f.write(f'Total analyses: {total_analyses}\n')
            f.write('Database count functions work correctly!\n')
        finally:
            db.close()
            
    except Exception as e:
        f.write(f'Error testing database functions: {e}\n')
        import traceback
        f.write(traceback.format_exc() + '\n')

print(f'Stats test results written to {result_file}')