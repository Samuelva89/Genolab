"""
Script para crear la base de datos y tablas necesarias.
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

def create_db():
    # Crear el motor de la base de datos
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)

    # Crear todas las tablas
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente!")

def create_default_user():
    """Crear un usuario predeterminado si no existe"""
    from app.database import SessionLocal
    from app import crud
    from app.schemas import UserCreate

    db = SessionLocal()
    try:
        # Verificar si ya existe algún usuario
        existing_user = db.query(User).first()

        if not existing_user:
            print("Creando usuario predeterminado...")
            # Crear usuario predeterminado
            user_data = UserCreate(
                email="user@genolab.com",
                name="Usuario Predeterminado"
            )

            created_user = crud.create_user(db=db, user=user_data)
            db.add(created_user)
            db.commit()
            db.refresh(created_user)
            print(f"Usuario predeterminado creado: {created_user.email}")
        else:
            print(f"Usuario ya existe: {existing_user.email}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Inicializando la base de datos...")
    create_db()
    print("Creando usuario predeterminado...")
    create_default_user()

    print("¡Base de datos inicializada exitosamente!")