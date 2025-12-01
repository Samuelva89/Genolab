"""
Script para probar la subida de archivos con un usuario ya existente
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.app.database import Base
from services.app import models, crud
from services.app.schemas import UserCreate

# Usar la misma URL de base de datos que el sistema
SQLALCHEMY_DATABASE_URL = "sqlite:///./services/data/genolab.db"  # Ajustado a la ubicación persistente
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_user():
    """Crear un usuario de prueba en la base de datos"""
    db = SessionLocal()
    try:
        # Verificar si ya existe algún usuario
        existing_user = db.query(models.User).first()
        if existing_user:
            print(f"Usuario existente encontrado: {existing_user.email}")
            return existing_user.id

        # Crear nuevo usuario de prueba
        user_data = UserCreate(
            email="test@example.com",
            name="Test User"
        )
        user = crud.create_user(db, user_data)
        print(f"Usuario creado: {user.email} con ID: {user.id}")
        return user.id
    except Exception as e:
        print(f"Error creando usuario: {e}")
        return None
    finally:
        db.close()

def main():
    print("Creando usuario de prueba...")
    user_id = create_test_user()

    if user_id:
        print(f"OK Usuario listo con ID: {user_id}")
        print("Ahora puedes ejecutar las pruebas de subida de archivos")
        print("El problema de 'No hay usuarios en la base de datos' debería estar resuelto")
    else:
        print("XXX Error: No se pudo crear el usuario de prueba")

if __name__ == "__main__":
    main()