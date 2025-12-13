#!/bin/bash
set -e  # Exit on any error

echo "Starting Genolab API deployment with MySQL..."

# Change to the services directory
cd /opt/render/project/src/services

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Wait for MySQL database to be ready
echo "Waiting for MySQL database to be ready..."
python -c "
import time
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from app.core.config import settings

max_attempts = 30
attempt = 0
while attempt < max_attempts:
    try:
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
        with engine.connect() as conn:
            conn.execute('SELECT 1')
        print('MySQL database connection successful!')
        break
    except OperationalError as e:
        print(f'MySQL database not ready, attempt {attempt+1}/{max_attempts}: {e}')
        time.sleep(10)
        attempt += 1
else:
    print('Failed to connect to MySQL database after max attempts')
    sys.exit(1)
"

# Create/update database tables
echo "Initializing MySQL database tables..."
python create_db.py

# Start the application server
echo "Starting Genolab API server..."
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:$PORT --timeout 120 --access-logfile - --error-logfile -