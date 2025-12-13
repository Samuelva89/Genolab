"""
Script para insertar análisis de ejemplo en la base de datos.
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

def insert_sample_analyses():
    # Crear sesión de base de datos
    db = SessionLocal()

    try:
        print("Insertando análisis de ejemplo...")

        # Obtener todas las cepas y usuarios existentes
        strains = crud.get_strains(db, skip=0, limit=10)
        users = crud.get_users(db, skip=0, limit=10)

        if not strains:
            print("No hay cepas para asociar análisis")
            return

        if not users:
            print("No hay usuarios para asociar análisis")
            return

        # Insertar análisis de ejemplo
        sample_analyses = [
            {
                "analysis_type": "fasta_count",
                "results": {"sequence_count": 42, "filename": "example.fasta", "upload_status": "completed"},
                "strain_id": strains[0].id,
                "file_url": "http://localhost:9001/genolab-bucket/uploads/example.fasta"
            },
            {
                "analysis_type": "fasta_gc_content",
                "results": {"filename": "example.fasta", "sequence_count": 1, "average_gc_content": 52.3, "individual_gc_contents": [52.3]},
                "strain_id": strains[1].id,
                "file_url": "http://localhost:9001/genolab-bucket/uploads/example2.fasta"
            },
            {
                "analysis_type": "raw_file",
                "results": {"filename": "raw_sequence.fasta", "file_size": 1024, "upload_status": "completed", "message": "Archivo subido directamente sin análisis"},
                "strain_id": strains[2].id,
                "file_url": "http://localhost:9001/genolab-bucket/uploads/raw_sequence.fasta"
            }
        ]

        for analysis_data in sample_analyses:
            analysis_in = schemas.AnalysisCreate(
                analysis_type=analysis_data["analysis_type"],
                results=analysis_data["results"],
                strain_id=analysis_data["strain_id"],
                file_url=analysis_data["file_url"]
            )

            analysis = crud.create_analysis(db, analysis_in, users[0].id)
            print(f"Análisis creado: {analysis.analysis_type} para cepa {analysis.strain_id}")

        print("Análisis de ejemplo insertados exitosamente!")

    except Exception as e:
        print(f"Error al insertar análisis de ejemplo: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_sample_analyses()