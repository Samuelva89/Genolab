@echo off
REM Script para inicializar la base de datos y arrancar la aplicación en Windows

echo Iniciando proceso de inicialización...

REM Crear la base de datos y tablas
echo Creando base de datos...
python create_db.py

REM Arrancar la aplicación FastAPI
echo Arrancando la aplicación...
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload