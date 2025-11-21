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
from app.models import User
from app import crud    
from app.schemas import UserCreate
import hashlib

def create_db():
    # Crear el motor de la base de datos
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
    
    # Crear todas las tablas
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente!")

def create_admin_user():
    """Crear un usuario administrador si no existe"""
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Verificar si ya existe un usuario administrador
        admin_user = db.query(User).first()
        
        if not admin_user:
            print("Creando usuario administrador predeterminado...")
            # Crear usuario administrador
            admin_data = UserCreate(
                email="admin@fungilap.com",
                name="Admin User",
                password="admin123"  # Cambiar en producción
            )
            
            admin_user = crud.create_user(db=db, user=admin_data)
            admin_user.is_admin = True
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"Usuario administrador creado: {admin_user.email}")
        else:
            print(f"Usuario administrador ya existe: {admin_user.email}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Inicializando la base de datos...")
    create_db()
    print("Creando usuario administrador...")
    create_admin_user()
    
    print("¡Base de datos inicializada exitosamente!")