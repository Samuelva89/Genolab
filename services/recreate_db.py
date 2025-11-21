"""
Script para recrear la base de datos con la nueva estructura (sin campo is_admin).
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Agregar la carpeta services al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.database import Base
from app.models import User, Organism, Strain, Analysis  # Importar todos los modelos

def recreate_db():
    # Crear el motor de la base de datos
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
    
    print("Eliminando y creando tablas en la base de datos...")
    # Eliminar todas las tablas
    Base.metadata.drop_all(bind=engine)
    # Crear todas las tablas con la nueva estructura
    Base.metadata.create_all(bind=engine)
    print("Tablas recreadas exitosamente!")

if __name__ == "__main__":
    recreate_db()