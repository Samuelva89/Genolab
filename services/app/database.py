# Importaciones necesarias de SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .core.config import settings # <-- IMPORTACIÓN AÑADIDA

# --- Creación del Motor de la Base de Datos ---
# Aquí se usa la URL que definimos en el archivo de configuración.
# El argumento connect_args es específico y necesario para SQLite.
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30  # Aumentar timeout para evitar errores de database locked
    },
    pool_pre_ping=True  # Verificar conexiones antes de usarlas
)

# --- Creación de la Fábrica de Sesiones ---
# SessionLocal será la clase que usaremos para crear nuestras sesiones de BD.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Creación de la Base para los Modelos ---
# Nuestros modelos de SQLAlchemy heredarán de esta clase.
Base = declarative_base()