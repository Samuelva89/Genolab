@echo off
REM Script para inicializar la base de datos y arrancar la aplicación en Windows

echo Iniciando proceso de inicialización...

REM Crear la base de datos y tablas
echo Creando base de datos...
python create_db.py

REM Insertar datos de ejemplo si la base de datos está vacía
echo Verificando si hay datos en la base de datos...
python -c "
import sys
import os
sys.path.insert(0, os.getcwd())
os.chdir(os.getcwd())

from app.database import SessionLocal
from app.models import Organism

db = SessionLocal()
try:
    organism_count = db.query(Organism).count()
    print(f'Numero de organismos en la base de datos: {organism_count}')

    if organism_count == 0:
        print('La base de datos esta vacia. Insertando datos de ejemplo...')
        from insert_sample_data import insert_sample_data
        insert_sample_data()
    else:
        print('La base de datos ya contiene datos.')
finally:
    db.close()
"

REM Arrancar la aplicación FastAPI
echo Arrancando la aplicación...
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload