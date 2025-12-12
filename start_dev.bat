# Script para lanzar GENOLAB en modo desarrollo

echo "Iniciando GENOLAB en modo desarrollo..."

# Iniciar los servicios de docker-compose
echo "Iniciando servicios de backend..."
docker-compose up -d --build

# Esperar un poco para que los servicios se inicien
echo "Esperando a que los servicios se inicien..."
sleep 10

# Verificar estado de los contenedores
echo "Estado de los contenedores:"
docker-compose ps

echo ""
echo "Para acceder a la aplicación:"
echo "- Frontend: http://localhost:8080"
echo "- Backend API: http://localhost:8000/docs"
echo ""
echo "Para detener los servicios, ejecute: docker-compose down"