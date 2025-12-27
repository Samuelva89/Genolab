@echo off
REM Script para iniciar la aplicación Genolab con Docker Compose en Windows

echo Deteniendo contenedores existentes...
docker-compose down

echo Construyendo y levantando los servicios...
docker-compose up --build -d

echo Esperando a que los servicios estén listos...

REM Esperar un poco para que los servicios se inicien
timeout /t 10 /nobreak >nul

echo.
echo Verificando estado de los servicios...
docker-compose ps

echo.
echo Frontend disponible en: http://localhost:8080
echo Backend disponible en: http://localhost:8000
echo.
echo Para ver los logs: docker-compose logs -f
echo.
echo Presiona cualquier tecla para salir...
pause >nul