#!/bin/bash
set -e  # Exit on any error

echo "Starting Genolab API deployment with SQLite..."

# Change to the services directory
cd /opt/render/project/src/services

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# For SQLite, ensure the database path exists and is writable
echo "Ensuring SQLite database directory exists..."
mkdir -p "$(dirname "$(/opt/render/project/env/bin/python -c "from app.core.config import settings; print(settings.SQLALCHEMY_DATABASE_URL[10:])"))" 2>/dev/null || true

echo "Initializing SQLite database tables..."
python create_db.py

# Restore data from backup if available
echo "Checking for backup files to restore..."
if [ -f "backup_users.json" ] && [ -f "backup_organisms.json" ] && [ -f "backup_strains.json" ] && [ -f "backup_analyses.json" ]; then
    echo "Restoring data from backup files..."
    python restore_data.py restore
else
    echo "No backup files found to restore."
fi

# Start the application server
echo "Starting Genolab API server..."
exec gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:$PORT --timeout 120 --workers-per-core 1 --access-logfile - --error-logfile -