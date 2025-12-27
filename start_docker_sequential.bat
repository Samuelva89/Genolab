@echo off
REM Script para iniciar la aplicación Genolab con Docker Compose en Windows

echo Deteniendo contenedores existentes...
docker-compose down

echo Iniciando servicios en orden...
echo Iniciando Redis...
docker-compose up -d redis

echo Esperando a que Redis esté listo...
timeout /t 10 /nobreak >nul

echo Iniciando MinIO...
docker-compose up -d minio

echo Esperando a que MinIO esté listo (esto puede tomar un momento)...
timeout /t 30 /nobreak >nul

echo Iniciando Backend...
docker-compose up -d backend

echo Esperando a que Backend esté listo...
timeout /t 30 /nobreak >nul

echo Iniciando Worker...
docker-compose up -d worker

echo Iniciando Frontend...
docker-compose up -d frontend

echo.
echo Servicios iniciados. Verificando estado...
docker-compose ps

echo.
echo Frontend disponible en: http://localhost:8080
echo Backend disponible en: http://localhost:8000
echo MinIO disponible en: http://localhost:9000 (console en :9001)
echo.
echo Para ver los logs: docker-compose logs -f
echo.
echo Presiona cualquier tecla para salir...
pause >nul