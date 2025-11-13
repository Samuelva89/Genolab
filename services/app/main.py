# Importaciones necesarias
import os
from fastapi import FastAPI, APIRouter
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .database import engine # Importamos el motor de la BD y la Base de los modelos
from . import models  # Importamos los modelos para que SQLAlchemy los conozca
from .celery_worker import celery_app # Importamos la instancia de Celery
from fastapi.middleware.cors import CORSMiddleware
from .routers import users, auth, organisms, analysis

# --- Creación de las tablas en la Base de Datos ---
# Esta línea es CRÍTICA. Le dice a SQLAlchemy que cree todas las tablas
# que hemos definido en nuestros modelos (User, Organism, Strain)
# usando el motor (engine) que configuramos.
# Esto solo se ejecuta una vez al iniciar la aplicación.
models.Base.metadata.create_all(bind=engine)

# --- Configuración de Rate Limiting ---
# Limita las peticiones por IP para prevenir abusos y ataques de fuerza bruta
# Deshabilitado en modo testing
testing_mode = os.getenv("TESTING", "False").lower() == "true"

if not testing_mode:
    limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
else:
    # En modo testing, sin límites
    limiter = Limiter(key_func=get_remote_address, enabled=False)

# --- Instancia de la Aplicación FastAPI ---
# Aquí creamos la aplicación principal.
# La metadata que se añade aquí (title, version, description)
# aparecerá en la documentación automática de la API (en /docs).
app = FastAPI(
  title="FunjiLapV1 API",
  version="0.3.0", # Subí la versión por la nueva funcionalidad de admin
  description="Una API para gestionar un cepario de organismos (FunjiLapV1) y realizar análisis bioinformáticos.",
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
api_router.include_router(auth.router)
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
