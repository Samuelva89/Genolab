#!/bin/bash
# Script para iniciar la aplicación Genolab con Docker Compose

echo "Deteniendo contenedores existentes..."
docker-compose down

echo "Construyendo y levantando los servicios..."
docker-compose up --build -d

echo "Esperando a que los servicios estén listos..."

# Esperar a que el backend esté listo
echo "Esperando a que el backend esté listo..."
timeout=60
count=0
while [ $count -lt $timeout ]; do
  if docker-compose exec backend curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "Backend está listo."
    break
  else
    echo "Esperando al backend... ($count/$timeout)"
    sleep 5
    ((count++))
  fi
done

if [ $count -eq $timeout ]; then
  echo "Advertencia: El backend no respondió después de $timeout intentos."
else
  echo "Todos los servicios están listos."
  echo "Frontend disponible en: http://localhost:8080"
  echo "Backend disponible en: http://localhost:8000"
  echo ""
  echo "Para ver los logs: docker-compose logs -f"
fi