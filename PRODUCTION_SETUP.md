# Configuración de Producción - GENOLAB

## Variables de Entorno

### Backend (Python/FastAPI)
```bash
# Base de datos (usar PostgreSQL en producción en lugar de SQLite)
SQLALCHEMY_DATABASE_URL=postgresql://usuario:contraseña@localhost/genolab_db

# Credenciales de MinIO
MINIO_ENDPOINT=https://minio-tu-dominio.com
MINIO_ACCESS_KEY=tu_access_key_seguro
MINIO_SECRET_KEY=tu_secret_key_seguro
MINIO_BUCKET_NAME=genolab-bucket

# Configuración de Redis (broker para Celery)
REDIS_URL=redis://:clave_redis@redis-tu-dominio.com:6379/0

# JWT y seguridad
SECRET_KEY=clave_super_secreta_muy_larga_y_aleatoria
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Otros ajustes
DEBUG=False
TESTING=False
```

### Frontend (React)
```env
# URL del backend de producción
VITE_API_URL=https://api.genolab-tu-dominio.com

# Otros ajustes de frontend
VITE_APP_NAME=GENOLAB
VITE_ENV=production
```

## Docker Compose para Producción

```yaml
services:
  minio:
    image: quay.io/minio/minio:RELEASE.2023-09-07T02-05-02Z
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000" # Solo interno en producción
      - "9001:9001" # Consola (restringir acceso)
    volumes:
      - minio_data:/data
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    restart: always

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --requirepass ${REDIS_PASSWORD}
    restart: always

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: genolab_db
      POSTGRES_USER: genolab_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  app:
    build:
      context: ./services
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    environment:
      - SQLALCHEMY_DATABASE_URL=postgresql://genolab_user:${POSTGRES_PASSWORD}@postgres:5432/genolab_db
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - MINIO_ENDPOINT=http://minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
      - MINIO_BUCKET_NAME=${MINIO_BUCKET_NAME}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      minio:
        condition: service_healthy
    restart: always

  celery_worker:
    build:
      context: ./services
      dockerfile: Dockerfile.prod
    env_file:
      - .env.production
    environment:
      - SQLALCHEMY_DATABASE_URL=postgresql://genolab_user:${POSTGRES_PASSWORD}@postgres:5432/genolab_db
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - MINIO_ENDPOINT=http://minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
      - MINIO_BUCKET_NAME=${MINIO_BUCKET_NAME}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      minio:
        condition: service_healthy
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=${FRONTEND_API_URL}
    depends_on:
      - app
    restart: always

volumes:
  minio_data:
  redis_data:
  postgres_data:
```

## Scripts de Despliegue

### Script de build para producción
```bash
#!/bin/bash

echo "Building GENOLAB for production..."

# Validar existencia de .env
if [ ! -f .env.production ]; then
    echo "Error: archivo .env.production no encontrado"
    exit 1
fi

# Build del backend
cd services
docker build -f Dockerfile.prod -t genolab-backend:latest .
cd ..

# Build del frontend
cd frontend
docker build -f Dockerfile.prod --build-arg VITE_API_URL=${FRONTEND_API_URL} -t genolab-frontend:latest .
cd ..

echo "Build completado."
```

### Script de despliegue
```bash
#!/bin/bash

echo "Desplegando GENOLAB..."

# Cargar variables de entorno
export $(grep -v '^#' .env.production | xargs)

# Levantar servicios
docker-compose -f docker-compose.prod.yaml up -d

echo "Despliegue completado. La aplicación está disponible en http://localhost"
```

## Monitoreo y Logging

### Logging
- Configurar rotación de logs
- Usar sistema de logging centralizado (como ELK stack)
- Monitorear logs de seguridad

### Métricas
- Configurar Prometheus para métricas
- Configurar alertas para fallos críticos
- Supervisar uso de recursos

## Seguridad

### HTTPS
- Configurar certificado SSL/TLS
- Redirigir HTTP a HTTPS
- Configurar headers de seguridad

### Autenticación (falta implementar)
- Implementar JWT con tokens expirables
- Configurar refresh tokens
- Implementar políticas de contraseñas seguras

## Backup

### Base de Datos
```bash
#!/bin/bash
# Script de backup para PostgreSQL
pg_dump -h localhost -U genolab_user -d genolab_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### MinIO
```bash
#!/bin/bash
# Script para backup de MinIO
mc mirror minio/genolab-bucket /backup/minio/$(date +%Y%m%d_%H%M%S)
```

## Mantenimiento

### Actualizaciones
- Planificar ventanas de mantenimiento
- Tener procedimiento de rollback
- Probar actualizaciones en staging antes de producción

### Limpieza
- Configurar limpieza de logs antiguos
- Eliminar archivos temporales
- Optimizar base de datos periódicamente

## Consideraciones Finales

1. **Seguridad**: Asegurarse de implementar autenticación JWT antes de producción
2. **Escalabilidad**: Configurar balanceador de carga si se espera alto tráfico
3. **Disaster Recovery**: Tener plan de recuperación ante desastres
4. **Documentación**: Mantener actualizada la documentación para el equipo de operaciones