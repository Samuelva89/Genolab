# Importaciones necesarias
import os
from fastapi import FastAPI, APIRouter
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .celery_worker import celery_app # Importamos la instancia de Celery
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from .routers import users, auth, organisms, analysis
from contextlib import asynccontextmanager
import boto3
from botocore.exceptions import ClientError
from .core.config import settings

# --- Configuración de Rate Limiting ---
# Limita las peticiones por IP para prevenir abusos y ataques de fuerza bruta
# Deshabilitado en modo testing
testing_mode = os.getenv("TESTING", "False").lower() == "true"

if not testing_mode:
    limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
else:
    # En modo testing, sin límites
    limiter = Limiter(key_func=get_remote_address, enabled=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup, connect to MinIO and ensure the bucket exists.
    print("Attempting to connect to MinIO and verify bucket...")
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
        )

        bucket_name = settings.MINIO_BUCKET_NAME

        s3_client.head_bucket(Bucket=bucket_name)
        print(f"MinIO bucket '{bucket_name}' already exists.")

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == '404' or error_code == 'NoSuchBucket':
            print(f"MinIO bucket '{bucket_name}' not found. Attempting to create it...")
            try:
                s3_client.create_bucket(Bucket=bucket_name)
                print(f"MinIO bucket '{bucket_name}' created successfully.")
            except ClientError as create_error:
                print(f"CRITICAL: Failed to create MinIO bucket '{bucket_name}'. Error: {create_error}")
                # Still yield to let the app start, but the upload functionality will fail.
        else:
            # For other client errors (e.g., connection refused, invalid credentials)
            print(f"WARNING: Could not connect to MinIO or verify bucket. File uploads will fail. Error: {e}")

    except Exception as e:
        # Catch any other potential exceptions during S3 client initialization
        print(f"WARNING: An unexpected error occurred during MinIO initialization. File uploads will fail. Error: {e}")

    yield
    # Code below yield runs on shutdown
    print("Shutting down.")

# --- Instancia de la Aplicación FastAPI ---
# Aquí creamos la aplicación principal.
# La metadata que se añade aquí (title, version, description)
# aparecerá en la documentación automática de la API (en /docs).
app = FastAPI(
  title="FunjiLapV1 API",
  version="0.3.0", # Subí la versión por la nueva funcionalidad de admin
  description="Una API para gestionar un cepario de organismos (FunjiLapV1) y realizar análisis bioinformáticos.",
  lifespan=lifespan
)

# Configuración de CORS
origins = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:3000", # Puerto común para desarrollo de frontend
    "http://localhost:5173", # Puerto por defecto de Vite
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SlowAPIMiddleware)

# Agregar el limiter al estado de la aplicación
app.state.limiter = limiter

# Registrar el handler para cuando se exceda el rate limit (solo si no estamos en testing)
if not testing_mode:
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Configuración de Celery para autodetección de tareas ---
celery_app.autodiscover_tasks(['app'])

# --- Inclusión de Routers ---
# Aquí es donde conectamos los archivos de rutas a la aplicación principal.
# Se agrupan bajo un router principal para versionar la API con el prefijo /api/v1.


api_router = APIRouter(prefix="/api")

api_router.include_router(users.router)
# api_router.include_router(auth.router)  # Deshabilitado temporalmente
api_router.include_router(organisms.router)
api_router.include_router(analysis.router)

app.include_router(api_router)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# --- Ruta Raíz ---
# Esta es la primera ruta que alguien ve cuando visita la URL principal de la API.
@app.get("/")
def read_root():
    return {"message": "Bienvenido a FunjiLapV1 API. Visita /docs para ver la documentación."}
