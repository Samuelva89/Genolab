# Configuración del Proyecto FunjiLapV1 API

## Requisitos Previos

- Python 3.10 o superior
- Docker y Docker Compose
- Git

## Configuración Local

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd FUNJILAP/services
```

### 2. Configuración del Entorno

#### a. Variables de Entorno

Crea un archivo `.env` en la carpeta `services` basado en el archivo `.env.example`:

```bash
# Copiar el archivo de ejemplo
cp .env.example .env
```

Luego edita el archivo `.env` y asegúrate de tener al menos las siguientes variables configuradas:

```env
# Base de datos (SQLite por defecto para desarrollo)
SQLALCHEMY_DATABASE_URL=sqlite:///./fungilap.db

# MinIO (si estás usando Docker Compose, mantén estos valores)
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET_NAME=fungilap-bucket

# Redis (si estás usando Docker Compose, mantén estos valores)
REDIS_URL=redis://redis:6379/0
```

### 3. Instalación de Dependencias

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate
# o en Linux/Mac
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 4. Inicializar la Base de Datos

#### Opción A: Usando el script de inicialización

```bash
python create_db.py
```

#### Opción B: Usando Alembic (si usas PostgreSQL/MySQL)

```bash
# Generar migración inicial (si es necesario)
alembic revision --autogenerate -m "Initial migration"

# Aplicar migraciones
alembic upgrade head
```

### 5. Arrancar la Aplicación

#### Opción A: Directamente con Python (desarrollo)

```bash
# Con el entorno virtual activado
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Opción B: Con el script proporcionado (desarrollo)

```bash
# En Linux/Mac
./start_app.sh

# En Windows
start_app.bat
```

#### Opción C: Con Docker Compose (todo el sistema)

```bash
# En la raíz del proyecto (D:\FUNJILAP)
docker-compose up --build
```

## Configuración con Docker Compose

El proyecto está configurado para funcionar con Docker Compose. La configuración incluye:

- Aplicación FastAPI
- Servidor MinIO para almacenamiento de objetos
- Redis para tareas Celery
- Volúmenes persistentes para datos

Para arrancar todo el sistema:

```bash
docker-compose up --build
```

## Endpoints Importantes

- API: `http://localhost:8000`
- Documentación de la API (Swagger): `http://localhost:8000/docs`
- Documentación de la API (ReDoc): `http://localhost:8000/redoc`
- Consola MinIO: `http://localhost:9001`
- Health Check: `http://localhost:8000/api/health`

## Solución de Problemas

### Problemas Comunes:

1. **Error de conexión a la base de datos:**
   - Verifica que la variable `SQLALCHEMY_DATABASE_URL` esté correctamente configurada
   - Si usas SQLite, asegúrate que la ruta del archivo sea accesible
   - Si usas PostgreSQL/MySQL, verifica que el servidor esté corriendo

2. **Error con Alembic:**
   - Asegúrate de tener la variable `DATABASE_URL` o `SQLALCHEMY_DATABASE_URL` configurada
   - Verifica que puedas conectarte a la base de datos con los credenciales proporcionados

3. **Error con MinIO:**
   - Verifica que el servicio de MinIO esté corriendo
   - Comprueba que las credenciales de acceso sean correctas

4. **Error con Redis:**
   - Asegúrate que el servidor Redis esté disponible
   - Revisa la URL de conexión

### Verificar Configuración

Puedes verificar que todo esté funcionando correctamente con:

```bash
# Verificar conexión a la API
curl http://localhost:8000/

# Verificar health check
curl http://localhost:8000/api/health
```

## Seguridad

- En producción, cambia la `SECRET_KEY` por defecto
- Asegúrate de usar contraseñas seguras para todos los servicios
- Usa HTTPS para conexiones externas
- Revisa y actualiza regularmente las dependencias