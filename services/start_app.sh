#!/bin/sh

# Salir inmediatamente si un comando falla
set -e

# Establecer la variable PYTHONPATH para que pueda encontrar los módulos
export PYTHONPATH=/app/services:$PYTHONPATH

# Cambiar al directorio de servicios donde está el código
cd /app/services

# Asegurar que el directorio de la base de datos exista
echo "Creating database directory if it doesn't exist..."
mkdir -p /app/services/data

# Crear las tablas de la base de datos directamente usando Python
echo "Creating database tables..."
python -c "
import sys
import os
sys.path.insert(0, '/app/services')
os.chdir('/app/services')

# Importar y crear las tablas
from app.database import engine, Base
from sqlalchemy import text

print('Creating all tables...')
Base.metadata.create_all(bind=engine)
print('Tables created successfully!')
"

# Crear usuario predeterminado si no existe
echo "Creating default user if needed..."
python -c "
import sys
import os
sys.path.insert(0, '/app/services')
os.chdir('/app/services')

from app.database import SessionLocal
from app.models import User
from app import crud
from app.schemas import UserCreate

db = SessionLocal()
try:
    # Verificar si ya existe algún usuario
    existing_user = db.query(User).first()

    if not existing_user:
        print('Creating default user...')
        # Crear usuario predeterminado
        user_data = UserCreate(
            email='user@genolab.com',
            name='Usuario Predeterminado'
        )

        created_user = crud.create_user(db=db, user=user_data)
        db.add(created_user)
        db.commit()
        db.refresh(created_user)
        print(f'Default user created: {created_user.email}')
    else:
        print(f'User already exists: {existing_user.email}')
finally:
    db.close()
"

# Iniciar la aplicación con Uvicorn
echo 'Starting application...'
exec uvicorn app.main:app --host 0.0.0.0 --port 8000