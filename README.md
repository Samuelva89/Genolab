# Genolab - Genomic Laboratory Management System

Genolab es un sistema integral de gestión de laboratorio genómico construido con FastAPI, diseñado para administrar organismos, cepas y realizar análisis bioinformáticos.

## Despliegue con SQLite

Este repositorio contiene la configuración para desplegar con SQLite como base de datos principal, ideal para entornos de desarrollo y producción livianos.

## Tecnologías Usadas

- **Backend**: FastAPI (Python 3.11)
- **Base de datos**: SQLite (con persistencia en disco Render)
- **Cola de tareas**: Celery + Redis (opcional)
- **Almacenamiento de objetos**: MinIO (compatible con S3)
- **Despliegue**: Render
- **Frontend**: React + Vite

## Arquitectura de Despliegue

El sistema se despliega como dos servicios separados:
- **Backend (API)**: `genolab-api` - Servicio FastAPI con SQLite
- **Frontend**: `genolab-frontend` - Aplicación React servida por Nginx

## Configuración de Despliegue en Render

### Requisitos previos

1. Una cuenta Render (para uso institucional)
2. Acceso a un almacenamiento de objetos externo (MinIO/S3 bucket)
3. Repositorio GitHub con acceso configurado

### Pasos para el Despliegue Backend

1. Crea un nuevo Servicio Web en Render
2. Conecta con tu repositorio GitHub
3. Usa el archivo `render.yaml`
4. Configura las variables de entorno (ver más abajo)

### Pasos para el Despliegue Frontend

1. Crea un nuevo Servicio Web en Render
2. Conecta con tu repositorio GitHub
3. Usa el archivo `render-frontend.yaml`
4. El frontend obtiene automáticamente la URL del backend

### Variables de Entorno Backend

Configure las siguientes variables en el panel de Render:

- `SQLALCHEMY_DATABASE_URL`: sqlite:////var/lib/render/sqlite-data/genolab.db (configuración predeterminada)
- `REDIS_URL`: URL del servicio Redis (opcional, para Celery)
- `MINIO_ENDPOINT`: URL del endpoint de MinIO/S3
- `MINIO_ACCESS_KEY`: Clave de acceso para MinIO/S3
- `MINIO_SECRET_KEY`: Clave secreta para MinIO/S3
- `MINIO_BUCKET_NAME`: Nombre del bucket (por defecto: genolab-bucket)
- `SECRET_KEY`: Clave secreta JWT para autenticación (generar una clave segura)
- `ALGORITHM`: HS256
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 30
- `MAX_UPLOAD_SIZE_MB`: 10
- `ALLOWED_EXTENSIONS`: fasta,fastq,gb,gff,fa,fq
- `CORS_ALLOWED_ORIGINS`: https://genolab-frontend.onrender.com (para permitir solicitudes desde el frontend)

### Servicios Render

La configuración creará los siguientes servicios:
- **genolab-api**: Servicio web backend que ejecuta la aplicación FastAPI con SQLite
- **genolab-frontend**: Servicio web frontend que sirve la aplicación React

## Comandos de Desarrollo

- `npm run dev`: Iniciar el entorno completo con Docker
- `npm run dev:down`: Detener el entorno Docker
- `npm run backend`: Iniciar solo el backend
- `npm run frontend`: Iniciar solo el frontend
- `npm run backup:data`: Crear backup de los datos
- `npm run restore:data`: Restaurar datos desde backup

## Características de Seguridad

- Autenticación basada en JWT
- Limitación de tasa (60 solicitudes por minuto por IP)
- Validación de entrada con Pydantic
- Configuración basada en entorno
- CORS configurado para comunicación segura entre frontend y backend

## Persistencia de Datos

- **SQLite**: La base de datos se almacena en un disco persistente de Render para mantener los datos entre reinicios
- **Backups**: Archivos JSON de backup para restauración de datos
- **MinIO**: Almacenamiento persistente para archivos de análisis genómicos

## Documentación de la API

Una vez desplegado, la documentación de la API está disponible en:
- `/docs` - Documentación interactiva de la API (Swagger UI)
- `/redoc` - Documentación alternativa de la API (ReDoc)

## Soporte para Despliegue Institucional

Para soporte de despliegue institucional, contacta con tu departamento de TI para la configuración y asistencia con la cuenta Render.