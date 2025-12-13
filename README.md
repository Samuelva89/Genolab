# Genolab - Genomic Laboratory Management System

Genolab es un sistema integral de gestión de laboratorio genómico construido con FastAPI, diseñado para administrar organismos, cepas y realizar análisis bioinformáticos.

## Despliegue con MySQL

Este repositorio contiene la configuración para desplegar con MySQL como base de datos principal.

## Tecnologías Usadas

- **Backend**: FastAPI (Python 3.11)
- **Base de datos**: MySQL
- **Cola de tareas**: Celery + Redis
- **Almacenamiento de objetos**: MinIO (compatible con S3)
- **Despliegue**: Render

## Configuración de Despliegue en Render

### Requisitos previos

1. Una cuenta Render (para uso institucional)
2. Acceso a un almacenamiento de objetos externo (MinIO/S3 bucket)
3. Repositorio GitHub con acceso configurado

### Pasos para el Despliegue

1. Crea un nuevo Servicio Web en Render
2. Conecta con tu repositorio GitHub
3. Actualiza el archivo Blueprint de Configuración para usar `render.yaml`
4. Configura las variables de entorno (ver más abajo)

### Variables de Entorno

Configure las siguientes variables en el panel de Render:

- `SQLALCHEMY_DATABASE_URL`: Render lo configurará automáticamente desde el servicio de base de datos
- `REDIS_URL`: Render lo configurará automáticamente desde el servicio Redis
- `MINIO_ENDPOINT`: URL del endpoint de MinIO/S3
- `MINIO_ACCESS_KEY`: Clave de acceso para MinIO/S3
- `MINIO_SECRET_KEY`: Clave secreta para MinIO/S3
- `MINIO_BUCKET_NAME`: Nombre del bucket (por defecto: genolab-bucket)
- `SECRET_KEY`: Clave secreta JWT para autenticación (generar una clave segura)
- `ALGORITHM`: HS256
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 30
- `MAX_UPLOAD_SIZE_MB`: 10
- `ALLOWED_EXTENSIONS`: fasta,fastq,gb,gff,fa,fq

### Servicios Render

La configuración creará los siguientes servicios:
- **genolab-api-mysql**: Servicio web que ejecuta la aplicación FastAPI
- **genolab-mysql-db**: Servicio de base de datos MySQL
- **genolab-redis**: Servicio Redis para Celery

## Documentación de la API

Una vez desplegado, la documentación de la API está disponible en:
- `/docs` - Documentación interactiva de la API (Swagger UI)
- `/redoc` - Documentación alternativa de la API (ReDoc)

## Características de Seguridad

- Autenticación basada en JWT
- Limitación de tasa (60 solicitudes por minuto por IP)
- Hashing seguro de contraseñas con bcrypt
- Validación de entrada con Pydantic
- Configuración basada en entorno

## Soporte para Despliegue Institucional

Para soporte de despliegue institucional, contacta con tu departamento de TI para la configuración y asistencia con la cuenta Render.