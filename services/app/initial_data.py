"""
Script para inicializar la base de datos con datos iniciales.
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Agregar la carpeta app al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from database import Base
from models import User, Organism, Strain, Analysis  # Importar todos los modelos

def init_db():
    # Crear el motor de la base de datos
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
    
    # Crear todas las tablas
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente!")

if __name__ == "__main__":
    init_db()