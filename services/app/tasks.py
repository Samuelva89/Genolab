import io
import boto3
from sqlalchemy.orm import Session
from Bio import SeqIO
from BCBio import GFF # Necesario para gff_stats
import numpy as np # Necesario para cálculos estadísticos como la media
from collections import Counter # Necesario para gff_stats
import logging # <- Añadido
import traceback # <- Añadido

from .celery_worker import celery_app
from . import crud, schemas
from .database import SessionLocal # Necesario para crear sesiones de DB dentro de las tareas
from .core.config import settings # Import settings

# --- Configuración del Cliente MinIO/S3 ---
# Inicialización diferida para manejar problemas de inicio
def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY
    )

s3_client = None  # Inicializado como None para evitar problemas en la importación

# Función auxiliar para obtener una sesión de base de datos para las tareas
def get_db_task():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@celery_app.task(bind=True)
def process_fasta_count(self, strain_id: int, owner_id: int, bucket: str, object_key: str, analysis_type_str: str):
    db: Session = next(get_db_task())

    try:
        # Inicializar cliente S3
        s3_client = get_s3_client()

        # 1. Obtener stream del archivo desde MinIO y procesarlo
        response = s3_client.get_object(Bucket=bucket, Key=object_key)
        filename = object_key.split('/')[-1]
        text_stream = io.TextIOWrapper(response['Body'], encoding='utf-8')

        # 2. Verificación de la Cepa
        db_strain = crud.get_strain(db, strain_id=strain_id)
        if not db_strain:
            raise ValueError(f"La cepa con ID {strain_id} no existe.")

        # 3. Lectura y Análisis del Archivo (vía stream)
        sequence_count = 0
        for record in SeqIO.parse(text_stream, "fasta"):
            sequence_count += 1

        # 4. Guardado de Resultados
        analysis_results = {"sequence_count": sequence_count, "filename": filename}

        # Construir la URL del archivo para guardarla en la BD
        file_url = f"{settings.MINIO_ENDPOINT}/{bucket}/{object_key}"

        analysis_to_create = schemas.AnalysisCreate(
            analysis_type=analysis_type_str,
            results=analysis_results,
            strain_id=strain_id,
            file_url=file_url  # Pasamos la URL del archivo
        )

        created_analysis = crud.create_analysis(
            db=db, analysis=analysis_to_create, owner_id=owner_id
        )

        return {"status": "SUCCESS", "analysis_id": created_analysis.id}
    except Exception as e:
        # --- Lógica mejorada para manejar el fallo de la tarea ---
        db_except: Session = SessionLocal() # Nueva sesión para el manejo de errores
        try:
            logging.exception(f"Celery task '{self.request.id}' ({self.name}) failed for strain {strain_id}: {e}")
            self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e), 'traceback': traceback.format_exc()})

            error_details = {
                "status": "FAILED",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc(),
                "celery_task_id": self.request.id,
                "strain_id": strain_id,
                "owner_id": owner_id,
                "bucket": bucket,
                "object_key": object_key
            }

            failed_file_url = f"{settings.MINIO_ENDPOINT}/{bucket}/{object_key}" # Reconstruir URL si es posible

            failed_analysis_to_create = schemas.AnalysisCreate(
                analysis_type=analysis_type_str,
                results=error_details,
                strain_id=strain_id,
                file_url=failed_file_url
            )
            crud.create_analysis(db=db_except, analysis=failed_analysis_to_create, owner_id=owner_id)
        except Exception as db_e:
            logging.error(f"FATAL: Failed to record Celery task failure in DB for task {self.request.id}: {db_e}", exc_info=True)
        finally:
            db_except.close() # Asegurarse de cerrar la sesión de error

        return {"status": "FAILED", "error": str(e), "celery_task_id": self.request.id}

@celery_app.task(bind=True)
def process_fasta_gc_content(self, strain_id: int, owner_id: int, bucket: str, object_key: str, analysis_type_str: str):
    db: Session = next(get_db_task())

    try:
        # Inicializar cliente S3
        s3_client = get_s3_client()

        response = s3_client.get_object(Bucket=bucket, Key=object_key)
        filename = object_key.split('/')[-1]
        text_stream = io.TextIOWrapper(response['Body'], encoding='utf-8')

        db_strain = crud.get_strain(db, strain_id=strain_id)
        if not db_strain:
            raise ValueError(f"La cepa con ID {strain_id} no existe.")

        gc_contents = []
        sequence_count = 0

        for record in SeqIO.parse(text_stream, "fasta"):
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

        file_url = f"{settings.MINIO_ENDPOINT}/{bucket}/{object_key}"
        analysis_to_create = schemas.AnalysisCreate(
            analysis_type=analysis_type_str,
            results=analysis_results,
            strain_id=strain_id,
            file_url=file_url
        )
        created_analysis = crud.create_analysis(
            db=db, analysis=analysis_to_create, owner_id=owner_id
        )
        return {"status": "SUCCESS", "analysis_id": created_analysis.id}
    except Exception as e:
        # --- Lógica mejorada para manejar el fallo de la tarea ---
        db_except: Session = SessionLocal() # Nueva sesión para el manejo de errores
        try:
            logging.exception(f"Celery task '{self.request.id}' ({self.name}) failed for strain {strain_id}: {e}")
            self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e), 'traceback': traceback.format_exc()})

            error_details = {
                "status": "FAILED",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc(),
                "celery_task_id": self.request.id,
                "strain_id": strain_id,
                "owner_id": owner_id,
                "bucket": bucket,
                "object_key": object_key
            }

            failed_file_url = f"{settings.MINIO_ENDPOINT}/{bucket}/{object_key}" # Reconstruir URL si es posible

            failed_analysis_to_create = schemas.AnalysisCreate(
                analysis_type=analysis_type_str,
                results=error_details,
                strain_id=strain_id,
                file_url=failed_file_url
            )
            crud.create_analysis(db=db_except, analysis=failed_analysis_to_create, owner_id=owner_id)
        except Exception as db_e:
            logging.error(f"FATAL: Failed to record Celery task failure in DB for task {self.request.id}: {db_e}", exc_info=True)
        finally:
            db_except.close() # Asegurarse de cerrar la sesión de error

        return {"status": "FAILED", "error": str(e), "celery_task_id": self.request.id}

@celery_app.task(bind=True)
def process_fastq_stats(self, strain_id: int, owner_id: int, bucket: str, object_key: str, analysis_type_str: str):
    db: Session = next(get_db_task())

    try:
        # Inicializar cliente S3
        s3_client = get_s3_client()

        response = s3_client.get_object(Bucket=bucket, Key=object_key)
        filename = object_key.split('/')[-1]
        text_stream = io.TextIOWrapper(response['Body'], encoding='utf-8')

        db_strain = crud.get_strain(db, strain_id=strain_id)
        if not db_strain:
            raise ValueError(f"La cepa con ID {strain_id} no existe.")

        sequence_count = 0
        all_lengths = []
        all_avg_qualities = []

        for record in SeqIO.parse(text_stream, "fastq"):
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

        file_url = f"{settings.MINIO_ENDPOINT}/{bucket}/{object_key}"
        analysis_to_create = schemas.AnalysisCreate(
            analysis_type=analysis_type_str,
            results=analysis_results,
            strain_id=strain_id,
            file_url=file_url
        )

        created_analysis = crud.create_analysis(
            db=db, analysis=analysis_to_create, owner_id=owner_id
        )
        return {"status": "SUCCESS", "analysis_id": created_analysis.id}
    except Exception as e:
        # --- Lógica mejorada para manejar el fallo de la tarea ---
        db_except: Session = SessionLocal() # Nueva sesión para el manejo de errores
        try:
            logging.exception(f"Celery task '{self.request.id}' ({self.name}) failed for strain {strain_id}: {e}")
            self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e), 'traceback': traceback.format_exc()})

            error_details = {
                "status": "FAILED",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc(),
                "celery_task_id": self.request.id,
                "strain_id": strain_id,
                "owner_id": owner_id,
                "bucket": bucket,
                "object_key": object_key
            }

            failed_file_url = f"{settings.MINIO_ENDPOINT}/{bucket}/{object_key}" # Reconstruir URL si es posible

            failed_analysis_to_create = schemas.AnalysisCreate(
                analysis_type=analysis_type_str,
                results=error_details,
                strain_id=strain_id,
                file_url=failed_file_url
            )
            crud.create_analysis(db=db_except, analysis=failed_analysis_to_create, owner_id=owner_id)
        except Exception as db_e:
            logging.error(f"FATAL: Failed to record Celery task failure in DB for task {self.request.id}: {db_e}", exc_info=True)
        finally:
            db_except.close() # Asegurarse de cerrar la sesión de error

        return {"status": "FAILED", "error": str(e), "celery_task_id": self.request.id}

@celery_app.task(bind=True)
def process_genbank_stats(self, strain_id: int, owner_id: int, bucket: str, object_key: str, analysis_type_str: str):
    db: Session = next(get_db_task())

    try:
        # Inicializar cliente S3
        s3_client = get_s3_client()

        response = s3_client.get_object(Bucket=bucket, Key=object_key)
        filename = object_key.split('/')[-1]
        text_stream = io.TextIOWrapper(response['Body'], encoding='utf-8')

        db_strain = crud.get_strain(db, strain_id=strain_id)
        if not db_strain:
            raise ValueError(f"La cepa con ID {strain_id} no existe.")

        records = list(SeqIO.parse(text_stream, "genbank"))
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

        file_url = f"{settings.MINIO_ENDPOINT}/{bucket}/{object_key}"
        analysis_to_create = schemas.AnalysisCreate(
            analysis_type=analysis_type_str,
            results=analysis_results,
            strain_id=strain_id,
            file_url=file_url
        )

        created_analysis = crud.create_analysis(
            db=db, analysis=analysis_to_create, owner_id=owner_id
        )
        return {"status": "SUCCESS", "analysis_id": created_analysis.id}
    except Exception as e:
        # --- Lógica mejorada para manejar el fallo de la tarea ---
        db_except: Session = SessionLocal() # Nueva sesión para el manejo de errores
        try:
            logging.exception(f"Celery task '{self.request.id}' ({self.name}) failed for strain {strain_id}: {e}")
            self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e), 'traceback': traceback.format_exc()})

            error_details = {
                "status": "FAILED",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc(),
                "celery_task_id": self.request.id,
                "strain_id": strain_id,
                "owner_id": owner_id,
                "bucket": bucket,
                "object_key": object_key
            }

            failed_file_url = f"{settings.MINIO_ENDPOINT}/{bucket}/{object_key}" # Reconstruir URL si es posible

            failed_analysis_to_create = schemas.AnalysisCreate(
                analysis_type=analysis_type_str,
                results=error_details,
                strain_id=strain_id,
                file_url=failed_file_url
            )
            crud.create_analysis(db=db_except, analysis=failed_analysis_to_create, owner_id=owner_id)
        except Exception as db_e:
            logging.error(f"FATAL: Failed to record Celery task failure in DB for task {self.request.id}: {db_e}", exc_info=True)
        finally:
            db_except.close() # Asegurarse de cerrar la sesión de error

        return {"status": "FAILED", "error": str(e), "celery_task_id": self.request.id}

def process_features(features, feature_counts=None):
    """
    Procesa las features de un archivo GFF recursivamente
    """
    if feature_counts is None:
        feature_counts = Counter()

    for feature in features:
        # Contar el tipo de feature
        feature_counts[feature.type] += 1
        # Procesar subfeatures si existen
        if feature.sub_features:
            process_features(feature.sub_features, feature_counts)

    return feature_counts

@celery_app.task(bind=True)
def process_gff_stats(self, strain_id: int, owner_id: int, bucket: str, object_key: str, analysis_type_str: str):
    db: Session = next(get_db_task())

    try:
        # Inicializar cliente S3
        s3_client = get_s3_client()

        response = s3_client.get_object(Bucket=bucket, Key=object_key)
        filename = object_key.split('/')[-1]
        text_stream = io.TextIOWrapper(response['Body'], encoding='utf-8')

        db_strain = crud.get_strain(db, strain_id=strain_id)
        if not db_strain:
            raise ValueError(f"La cepa con ID {strain_id} no existe.")

        feature_counts = Counter()

        for rec in GFF.parse(text_stream):
            process_features(rec.features, feature_counts)

        if not feature_counts:
            raise ValueError("El archivo GFF no contiene features o está vacío.")

        analysis_results = {
            "filename": filename,
            "feature_counts": dict(feature_counts)
        }

        file_url = f"{settings.MINIO_ENDPOINT}/{bucket}/{object_key}"
        analysis_to_create = schemas.AnalysisCreate(
            analysis_type=analysis_type_str,
            results=analysis_results,
            strain_id=strain_id,
            file_url=file_url
        )

        created_analysis = crud.create_analysis(
            db=db, analysis=analysis_to_create, owner_id=owner_id
        )
        return {"status": "SUCCESS", "analysis_id": created_analysis.id}
    except Exception as e:
        # --- Lógica mejorada para manejar el fallo de la tarea ---
        db_except: Session = SessionLocal() # Nueva sesión para el manejo de errores
        try:
            logging.exception(f"Celery task '{self.request.id}' ({self.name}) failed for strain {strain_id}: {e}")
            self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e), 'traceback': traceback.format_exc()})

            error_details = {
                "status": "FAILED",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc(),
                "celery_task_id": self.request.id,
                "strain_id": strain_id,
                "owner_id": owner_id,
                "bucket": bucket,
                "object_key": object_key
            }

            failed_file_url = f"{settings.MINIO_ENDPOINT}/{bucket}/{object_key}" # Reconstruir URL si es posible

            failed_analysis_to_create = schemas.AnalysisCreate(
                analysis_type=analysis_type_str,
                results=error_details,
                strain_id=strain_id,
                file_url=failed_file_url
            )
            crud.create_analysis(db=db_except, analysis=failed_analysis_to_create, owner_id=owner_id)
        except Exception as db_e:
            logging.error(f"FATAL: Failed to record Celery task failure in DB for task {self.request.id}: {db_e}", exc_info=True)
        finally:
            db_except.close() # Asegurarse de cerrar la sesión de error

        return {"status": "FAILED", "error": str(e), "celery_task_id": self.request.id}
