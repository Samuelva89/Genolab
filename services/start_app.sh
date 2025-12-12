#!/bin/bash
# Script para inicializar la base de datos y arrancar la aplicación

echo "Inicializando la base de datos..."

# Copiar archivos de backup desde el directorio de montaje si existen
if [ -d "/app/backup_files" ]; then
    echo "Copiando archivos de backup..."
    cp /app/backup_files/backup_*.json . 2>/dev/null || echo "No se encontraron archivos de backup en /app/backup_files"
else
    echo "No se encontró directorio de backup_files"
fi

# Crear la base de datos y tablas
echo "Creando estructura de la base de datos..."
python create_db.py

# Restaurar datos de backup si existen los archivos
echo "Restaurando datos de backup..."
python restore_data.py restore

echo "Arrancando la aplicación..."
uvicorn app.main:app --host 0.0.0.0 --port 8000