"""
Script para insertar más análisis de ejemplo con datos variados para mejorar la visualización de gráficos
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime

# Agregar la carpeta services al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.database import SessionLocal
from app import crud, models, schemas

def insert_more_sample_analyses():
    # Crear sesión de base de datos
    db = SessionLocal()

    try:
        print("Insertando más análisis de ejemplo con datos variados...")

        # Obtener todas las cepas y usuarios existentes
        strains = crud.get_strains(db, skip=0, limit=10)
        users = crud.get_users(db, skip=0, limit=10)

        if not strains:
            print("No hay cepas para asociar análisis")
            return

        if not users:
            print("No hay usuarios para asociar análisis")
            return

        # Insertar más análisis de ejemplo con datos que permitan gráficos mejores
        more_sample_analyses = [
            # Más análisis FASTA count con diferentes conteos
            {
                "analysis_type": "fasta_count",
                "results": {"sequence_count": 5, "filename": "more_sequences.fasta", "upload_status": "completed"},
                "strain_id": strains[0].id,
                "file_url": "http://localhost:9000/genolab-bucket/uploads/more_sequences.fasta"
            },
            {
                "analysis_type": "fasta_count",
                "results": {"sequence_count": 8, "filename": "many_sequences.fasta", "upload_status": "completed"},
                "strain_id": strains[1].id,
                "file_url": "http://localhost:9000/genolab-bucket/uploads/many_sequences.fasta"
            },
            # Más análisis de GC content con diferentes valores
            {
                "analysis_type": "fasta_gc_content",
                "results": {
                    "filename": "diverse_gc.fasta", 
                    "sequence_count": 4, 
                    "average_gc_content": 45.2, 
                    "individual_gc_contents": [42.1, 46.8, 47.3, 44.6]
                },
                "strain_id": strains[0].id,
                "file_url": "http://localhost:9000/genolab-bucket/uploads/diverse_gc.fasta"
            },
            {
                "analysis_type": "fasta_gc_content",
                "results": {
                    "filename": "high_gc.fasta", 
                    "sequence_count": 3, 
                    "average_gc_content": 68.7, 
                    "individual_gc_contents": [65.2, 71.3, 69.6]
                },
                "strain_id": strains[2].id,
                "file_url": "http://localhost:9000/genolab-bucket/uploads/high_gc.fasta"
            },
            # Más análisis GFF con diferentes features
            {
                "analysis_type": "gff_stats",
                "results": {
                    "filename": "complex_features.gff", 
                    "feature_counts": {"gene": 5, "mRNA": 5, "exon": 23, "CDS": 18, "intron": 19, "five_prime_UTR": 5, "three_prime_UTR": 5}
                },
                "strain_id": strains[1].id,
                "file_url": "http://localhost:9000/genolab-bucket/uploads/complex_features.gff"
            },
            {
                "analysis_type": "gff_stats",
                "results": {
                    "filename": "simple_features.gff", 
                    "feature_counts": {"gene": 2, "mRNA": 2, "exon": 8, "CDS": 6}
                },
                "strain_id": strains[2].id,
                "file_url": "http://localhost:9000/genolab-bucket/uploads/simple_features.gff"
            },
            # Análisis FASTQ con estadísticas
            {
                "analysis_type": "fastq_stats",
                "results": {
                    "filename": "quality_sample.fastq",
                    "sequence_count": 100,
                    "avg_sequence_length": 150.5,
                    "min_length": 148,
                    "max_length": 154,
                    "overall_avg_quality": 35.2
                },
                "strain_id": strains[0].id,
                "file_url": "http://localhost:9000/genolab-bucket/uploads/quality_sample.fastq"
            },
            # Análisis GenBank con más detalles
            {
                "analysis_type": "genbank_stats",
                "results": {
                    "filename": "detailed_sequence.gbk",
                    "sequence_count": 1,
                    "main_record_id": "NC_000001.1",
                    "description": "Chromosome 1 reference sequence",
                    "sequence_length": 248956422,
                    "feature_count": 4500,
                    "molecule_type": "DNA",
                    "topology": "linear"
                },
                "strain_id": strains[1].id,
                "file_url": "http://localhost:9000/genolab-bucket/uploads/detailed_sequence.gbk"
            }
        ]

        for analysis_data in more_sample_analyses:
            analysis_in = schemas.AnalysisCreate(
                analysis_type=analysis_data["analysis_type"],
                results=analysis_data["results"],
                strain_id=analysis_data["strain_id"],
                file_url=analysis_data["file_url"]
            )

            analysis = crud.create_analysis(db, analysis_in, users[0].id)
            print(f"Más análisis creados: {analysis.analysis_type} para cepa {analysis.strain_id}")

        print("¡Más análisis de ejemplo insertados exitosamente!")

    except Exception as e:
        print(f"Error al insertar más análisis de ejemplo: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_more_sample_analyses()