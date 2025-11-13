import io
from sqlalchemy.orm import Session
from Bio import SeqIO
from BCBio import GFF # Necesario para gff_stats
import numpy as np # Necesario para cálculos estadísticos como la media
from collections import Counter # Necesario para gff_stats

from .celery_worker import celery_app
from . import crud, schemas
from .database import SessionLocal # Necesario para crear sesiones de DB dentro de las tareas

# Función auxiliar para obtener una sesión de base de datos para las tareas
def get_db_task():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@celery_app.task(bind=True) # 'bind=True' permite acceder a la instancia de la tarea (self)
def process_fasta_count(self, strain_id: int, file_content: bytes, filename: str, owner_id: int):
    db: Session = next(get_db_task()) # Obtener una sesión de DB para esta tarea
    
    try:
        # 1. Verificación de la Cepa
        db_strain = crud.get_strain(db, strain_id=strain_id)
        if not db_strain:
            # Si la cepa no existe, la tarea falla
            raise ValueError(f"La cepa con ID {strain_id} no existe.")

        # 2. Lectura y Análisis del Archivo
        sequence_count = 0
        fasta_str = file_content.decode("utf-8")
        fasta_io = io.StringIO(fasta_str)
        
        for record in SeqIO.parse(fasta_io, "fasta"):
            sequence_count += 1

        # 3. Guardado de Resultados
        analysis_results = {"sequence_count": sequence_count, "filename": filename}
        
        analysis_to_create = schemas.AnalysisCreate(
            analysis_type="fasta_count",
            results=analysis_results,
            strain_id=strain_id,
        )
        
        created_analysis = crud.create_analysis(
            db=db, analysis=analysis_to_create, owner_id=owner_id
        )
        
        return {"status": "SUCCESS", "analysis_id": created_analysis.id}
    except Exception as e:
        # Registrar el error y marcar la tarea como fallida
        print(f"Celery task failed: {e}")
        return {"status": "FAILED", "error": str(e)}
    finally:
        db.close()

@celery_app.task(bind=True)
def process_fasta_gc_content(self, strain_id: int, file_content: bytes, filename: str, owner_id: int):
    db: Session = next(get_db_task())

    try:
        db_strain = crud.get_strain(db, strain_id=strain_id)
        if not db_strain:
            raise ValueError(f"La cepa con ID {strain_id} no existe.")

        gc_contents = []
        sequence_count = 0

        fasta_str = file_content.decode("utf-8")
        fasta_io = io.StringIO(fasta_str)
        for record in SeqIO.parse(fasta_io, "fasta"):
            sequence_count += 1
            seq = str(record.seq).upper()
            g_count = seq.count('G')
            c_count = seq.count('C')
            total_bases = len(seq)
            if total_bases > 0:
                gc_percent = ((g_count + c_count) / total_bases) * 100
                gc_contents.append(gc_percent)
            else:
                gc_contents.append(0.0)

        if sequence_count == 0:
            raise ValueError("El archivo FASTA no contiene secuencias.")

        avg_gc_content = np.mean(gc_contents) if gc_contents else 0.0

        analysis_results = {
            "filename": filename,
            "sequence_count": sequence_count,
            "average_gc_content": round(avg_gc_content, 2),
            "individual_gc_contents": [round(gc, 2) for gc in gc_contents]
        }

        analysis_to_create = schemas.AnalysisCreate(
            analysis_type="fasta_gc_content",
            results=analysis_results,
            strain_id=strain_id,
        )
        created_analysis = crud.create_analysis(
            db=db, analysis=analysis_to_create, owner_id=owner_id
        )
        return {"status": "SUCCESS", "analysis_id": created_analysis.id}
    except Exception as e:
        print(f"Celery task failed: {e}")
        return {"status": "FAILED", "error": str(e)}
    finally:
        db.close()

@celery_app.task(bind=True)
def process_fastq_stats(self, strain_id: int, file_content: bytes, filename: str, owner_id: int):
    db: Session = next(get_db_task())

    try:
        db_strain = crud.get_strain(db, strain_id=strain_id)
        if not db_strain:
            raise ValueError(f"La cepa con ID {strain_id} no existe.")

        sequence_count = 0
        all_lengths = []
        all_avg_qualities = []

        fastq_str = file_content.decode("utf-8")
        fastq_io = io.StringIO(fastq_str)
        for record in SeqIO.parse(fastq_io, "fastq"):
            sequence_count += 1
            all_lengths.append(len(record.seq))
            quality_scores = record.letter_annotations["phred_quality"]
            if quality_scores:
                avg_quality = np.mean(quality_scores)
                all_avg_qualities.append(avg_quality)

        if sequence_count == 0:
            raise ValueError("El archivo FASTQ no contiene secuencias.")

        overall_avg_quality = np.mean(all_avg_qualities) if all_avg_qualities else 0
        avg_length = np.mean(all_lengths)
        
        analysis_results = {
            "filename": filename,
            "sequence_count": sequence_count,
            "avg_sequence_length": round(avg_length, 2),
            "min_length": min(all_lengths),
            "max_length": max(all_lengths),
            "overall_avg_quality": round(overall_avg_quality, 2)
        }
        
        analysis_to_create = schemas.AnalysisCreate(
            analysis_type="fastq_stats",
            results=analysis_results,
            strain_id=strain_id,
        )
        
        created_analysis = crud.create_analysis(
            db=db, analysis=analysis_to_create, owner_id=owner_id
        )
        return {"status": "SUCCESS", "analysis_id": created_analysis.id}
    except Exception as e:
        print(f"Celery task failed: {e}")
        return {"status": "FAILED", "error": str(e)}
    finally:
        db.close()

@celery_app.task(bind=True)
def process_genbank_stats(self, strain_id: int, file_content: bytes, filename: str, owner_id: int):
    db: Session = next(get_db_task())

    try:
        db_strain = crud.get_strain(db, strain_id=strain_id)
        if not db_strain:
            raise ValueError(f"La cepa con ID {strain_id} no existe.")

        gb_str = file_content.decode("utf-8")
        gb_io = io.StringIO(gb_str)
        
        records = list(SeqIO.parse(gb_io, "genbank"))
        if not records:
            raise ValueError("El archivo GenBank no contiene registros.")

        main_record = records[0]
        
        analysis_results = {
            "filename": filename,
            "sequence_count": len(records),
            "main_record_id": main_record.id,
            "description": main_record.description,
            "sequence_length": len(main_record.seq),
            "feature_count": len(main_record.features),
            "molecule_type": main_record.annotations.get('molecule_type', 'N/A'),
            "topology": main_record.annotations.get('topology', 'N/A'),
        }

        analysis_to_create = schemas.AnalysisCreate(
            analysis_type="genbank_stats",
            results=analysis_results,
            strain_id=strain_id,
        )
        
        created_analysis = crud.create_analysis(
            db=db, analysis=analysis_to_create, owner_id=owner_id
        )
        return {"status": "SUCCESS", "analysis_id": created_analysis.id}
    except Exception as e:
        print(f"Celery task failed: {e}")
        return {"status": "FAILED", "error": str(e)}
    finally:
        db.close()

@celery_app.task(bind=True)
def process_gff_stats(self, strain_id: int, file_content: bytes, filename: str, owner_id: int):
    db: Session = next(get_db_task())

    try:
        db_strain = crud.get_strain(db, strain_id=strain_id)
        if not db_strain:
            raise ValueError(f"La cepa con ID {strain_id} no existe.")

        feature_counts = Counter()

        gff_str = file_content.decode("utf-8")
        gff_io = io.StringIO(gff_str)

        def process_features(features):
            for feature in features:
                feature_counts[feature.type] += 1
                if feature.sub_features:
                    process_features(feature.sub_features)

        for rec in GFF.parse(gff_io):
            process_features(rec.features)

        if not feature_counts:
            raise ValueError("El archivo GFF no contiene features o está vacío.")

        analysis_results = {
            "filename": filename,
            "feature_counts": dict(feature_counts)
        }

        analysis_to_create = schemas.AnalysisCreate(
            analysis_type="gff_stats",
            results=analysis_results,
            strain_id=strain_id,
        )

        created_analysis = crud.create_analysis(
            db=db, analysis=analysis_to_create, owner_id=owner_id
        )
        return {"status": "SUCCESS", "analysis_id": created_analysis.id}
    except Exception as e:
        print(f"Celery task failed: {e}")
        return {"status": "FAILED", "error": str(e)}
    finally:
        db.close()
