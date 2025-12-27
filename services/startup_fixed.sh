#!/bin/bash
# Script de inicialización para asegurar que la base de datos esté lista

echo "Esperando a que MinIO esté listo..."
timeout=300  # 5 minutes timeout
count=0
while [ $count -lt $timeout ]; do
  if curl -f http://minio:9000/minio/health/live > /dev/null 2>&1; then
    echo "MinIO está listo."
    break
  fi
  echo "Esperando a MinIO... ($count segundos)"
  sleep 5
  count=$((count + 5))
done

if [ $count -ge $timeout ]; then
  echo "Tiempo de espera agotado para MinIO. Continuando de todos modos..."
else
  echo "MinIO está listo. Inicializando la base de datos..."
  python create_db.py
fi

echo "Iniciando la aplicación..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000