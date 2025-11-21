# Importaciones necesarias de SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .core.config import settings # <-- IMPORTACIÓN AÑADIDA

# --- Creación del Motor de la Base de Datos ---
# Usamos la URL de la base de datos desde nuestra configuración centralizada.
# Esto nos permite cambiar fácilmente entre SQLite, MySQL y PostgreSQL.
engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)

# --- Creación de la Fábrica de Sesiones ---
# SessionLocal será la clase que usaremos para crear nuestras sesiones de BD.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Creación de la Base para los Modelos ---
# Nuestros modelos de SQLAlchemy heredarán de esta clase.
Base = declarative_base()