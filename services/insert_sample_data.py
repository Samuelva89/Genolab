"""
Script para insertar datos de ejemplo en la base de datos.
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Agregar la carpeta services al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.database import SessionLocal
from app import crud, models, schemas

def insert_sample_data():
    # Crear sesión de base de datos
    db = SessionLocal()

    try:
        print("Insertando datos de ejemplo...")

        # Verificar si ya existen datos
        existing_users = crud.get_users(db, skip=0, limit=1)
        existing_organisms = crud.get_organisms(db, skip=0, limit=1)
        existing_strains = crud.get_strains(db, skip=0, limit=1)

        print(f"Usuarios existentes: {len(existing_users)}")
        print(f"Organismos existentes: {len(existing_organisms)}")
        print(f"Cepas existentes: {len(existing_strains)}")

        # Insertar usuario de ejemplo si no existe
        if not existing_users:
            print("Creando usuario de ejemplo...")
            user_in = schemas.UserCreate(
                email="admin@genolab.com",
                name="Administrador Genolab"
            )
            user = crud.create_user(db, user_in)
            print(f"Usuario creado: {user.email}")
        else:
            user = existing_users[0]

        # Insertar organismos de ejemplo si no existen
        if not existing_organisms:
            print("Creando organismos de ejemplo...")

            organisms_data = [
                {"name": "Aspergillus niger", "genus": "Aspergillus", "species": "niger"},
                {"name": "Saccharomyces cerevisiae", "genus": "Saccharomyces", "species": "cerevisiae"},
                {"name": "Candida albicans", "genus": "Candida", "species": "albicans"},
            ]

            for org_data in organisms_data:
                org_in = schemas.OrganismCreate(
                    name=org_data["name"],
                    genus=org_data["genus"],
                    species=org_data["species"]
                )
                organism = crud.create_organism(db, org_in)
                print(f"Organismo creado: {organism.name}")

        # Insertar cepas de ejemplo si no existen
        if not existing_strains:
            print("Creando cepas de ejemplo...")

            # Primero obtenemos los organismos que creamos
            organisms = crud.get_organisms(db, skip=0, limit=10)

            strains_data = [
                {"strain_name": "ATCC 10864", "source": "Colección de cultivos", "organism_id": organisms[0].id},
                {"strain_name": "NCYC 2672", "source": "Colección de levaduras", "organism_id": organisms[1].id},
                {"strain_name": "SC5314", "source": "Colección clínica", "organism_id": organisms[2].id},
            ]

            for strain_data in strains_data:
                strain_in = schemas.StrainCreate(
                    strain_name=strain_data["strain_name"],
                    source=strain_data["source"],
                    organism_id=strain_data["organism_id"]
                )
                strain = crud.create_strain(db, strain_in)
                print(f"Cepa creada: {strain.strain_name}")

        print("Datos de ejemplo insertados exitosamente!")

    except Exception as e:
        print(f"Error al insertar datos de ejemplo: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_sample_data()