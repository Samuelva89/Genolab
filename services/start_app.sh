#!/bin/bash
# Script para inicializar la base de datos y arrancar la aplicación

echo "Iniciando proceso de inicialización..."

# Crear la base de datos y tablas
echo "Creando base de datos..."
python recreate_db.py

# Arrancar la aplicación FastAPI
echo "Arrancando la aplicación..."
uvicorn app.main:app --host 0.0.0.0 --port 8000