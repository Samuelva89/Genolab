#!/bin/bash
set -e
# Script de inicialización para asegurar que la base de datos esté lista

echo "Esperando a que MinIO esté listo..."

# Using curl to check MinIO health endpoint (same as in docker-compose healthcheck)
timeout=30
count=0
while [ $count -lt $timeout ]; do
  if curl -f http://minio:9000/minio/health/live > /dev/null 2>&1; then
    echo "MinIO está listo."
    break
  else
    echo "Esperando a MinIO... ($count/$timeout)"
    sleep 5
    ((count++))
  fi
done

if [ $count -eq $timeout ]; then
  echo "Advertencia: No se pudo conectar a MinIO después de $timeout intentos. Continuando de todas formas..."
else
  echo "MinIO está listo. Inicializando la base de datos..."
fi

python create_db.py

# Insertar datos de ejemplo si la base de datos está vacía
echo "Verificando si hay datos en la base de datos..."
python -c "
import sys
import os
sys.path.insert(0, '/app')
os.chdir('/app')

from app.database import SessionLocal
from app.models import Organism

db = SessionLocal()
try:
    organism_count = db.query(Organism).count()
    print(f'Número de organismos en la base de datos: {organism_count}')

    if organism_count == 0:
        print('La base de datos está vacía. Insertando datos de ejemplo...')
        from insert_sample_data import insert_sample_data
        insert_sample_data()
    else:
        print('La base de datos ya contiene datos.')
finally:
    db.close()
"

echo "Iniciando la aplicación Uvicorn..."
export SQLALCHEMY_DATABASE_URL="sqlite:///./data/genolab.db"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info