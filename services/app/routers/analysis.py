# Importaciones de librerías estándar y de terceros
import os
import uuid
import boto3
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Response
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas
from ..dependencies import get_db
from ..core.config import settings
from ..core.validators import validate_file_extension_for_analysis_type
from ..tasks import process_fasta_count, process_fasta_gc_content, process_fastq_stats, process_genbank_stats, process_gff_stats
from ..celery_worker import celery_app

# --- Configuración del Cliente MinIO/S3 ---
def get_s3_client():
    """FastAPI dependency to get a boto3 S3 client."""
    return boto3.client(
        's3',
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        region_name='us-east-1'  # Puede ser cualquier región, MinIO no la usa
    )

S3_BUCKET_NAME = settings.MINIO_BUCKET_NAME

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
)

@router.get("/strain/{strain_id}", response_model=List[schemas.Analysis])
def get_analyses_for_strain(
    strain_id: int,
    db: Session = Depends(get_db),
):
    """
    Devuelve una lista de todos los análisis asociados a una cepa específica.
    """
    strain = crud.get_strain(db, strain_id=strain_id)
    if not strain:
        raise HTTPException(status_code=404, detail="Cepa no encontrada.")
    analyses = crud.get_analyses_by_strain(db, strain_id=strain_id)
    return analyses

@router.post("/upload/raw", status_code=status.HTTP_201_CREATED)
async def upload_raw_file(
    strain_id: int = Form(...),
    analysis_type: str = Form("raw_file"),  # Tipo de análisis genérico
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    s3_client = Depends(get_s3_client)
):
    """
    Endpoint para subir archivos sin análisis, simplemente para almacenarlos en MinIO.
    """
    if not crud.get_strain(db, strain_id=strain_id):
        raise HTTPException(status_code=404, detail="La cepa especificada no existe.")

    # Validar extensiones permitidas
    allowed_extensions = ['.fasta', '.fastq', '.gbk', '.gff', '.txt', '.fa', '.fas', '.mfasta', '.fna', '.faa']
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Extensión de archivo no permitida. Extensiones permitidas: {allowed_extensions}")

    object_key = f"uploads/{uuid.uuid4()}-{file.filename}"

    try:
        s3_client.upload_fileobj(file.file, S3_BUCKET_NAME, object_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir el archivo a MinIO: {e}")

    # Crear registro en la base de datos para hacer seguimiento del archivo
    first_user = db.query(models.User).first()
    if not first_user:
        raise HTTPException(status_code=500, detail="No hay usuarios en la base de datos para asociar el registro.")

    # Crear un registro de análisis con resultados mínimos
    analysis_results = {
        "filename": file.filename,
        "file_size": file.size if file.size else "unknown",
        "upload_status": "completed",
        "message": "Archivo subido directamente sin análisis"
    }

    file_url = f"{settings.MINIO_ENDPOINT}/{S3_BUCKET_NAME}/{object_key}"
    analysis_to_create = schemas.AnalysisCreate(
        analysis_type=analysis_type,
        results=analysis_results,
        strain_id=strain_id,
        file_url=file_url
    )

    created_analysis = crud.create_analysis(
        db=db, analysis=analysis_to_create, owner_id=first_user.id
    )

    return {
        "message": "Archivo subido exitosamente",
        "analysis_id": created_analysis.id,
        "file_url": file_url
    }

@router.post("/upload/fasta_count", status_code=status.HTTP_202_ACCEPTED)
async def upload_and_count_fasta(
    strain_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    s3_client = Depends(get_s3_client)  # <-- INJECTED DEPENDENCY
):
    """
    Endpoint para subir un archivo FASTA y contar el número de secuencias.
    """
    if not crud.get_strain(db, strain_id=strain_id):
        raise HTTPException(status_code=404, detail="La cepa especificada no existe.")
    validate_file_extension_for_analysis_type(file.filename, 'fasta')
    object_key = f"uploads/{uuid.uuid4()}-{file.filename}"

    try:
        s3_client.upload_fileobj(file.file, S3_BUCKET_NAME, object_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir el archivo a MinIO: {e}")

    first_user = db.query(models.User).first()
    if not first_user:
        raise HTTPException(status_code=500, detail="No hay usuarios en la base de datos para asociar el análisis.")

    task = process_fasta_count.delay(
        strain_id=strain_id,
        owner_id=first_user.id,
        bucket=S3_BUCKET_NAME,
        object_key=object_key,
        analysis_type_str="fasta_count"
    )
    return {"message": "Análisis de conteo FASTA iniciado", "task_id": task.id}

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Consulta el estado de una tarea de Celery.
    """
    task = celery_app.AsyncResult(task_id)
    state = task.state
    info = task.info
    response = {'state': state, 'status': str(info)}

    if state == 'PENDING':
        response['status'] = 'Pendiente...'
    elif state == 'PROGRESS':
        response['status'] = info.get('status', 'Procesando...')
        response['progress'] = info.get('progress', 0)
    elif state == 'SUCCESS':
        response['status'] = 'Completado'
        response['result'] = task.result
    elif state == 'FAILURE':
        response['status'] = 'Fallido'
        response['error'] = str(info)

    return response

@router.post("/upload/fasta_gc_content", status_code=status.HTTP_202_ACCEPTED)
async def upload_and_analyze_fasta_gc_content(
    strain_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    s3_client = Depends(get_s3_client)  # <-- INJECTED DEPENDENCY
):
    """
    Endpoint para subir un archivo FASTA y calcular el contenido GC.
    """
    if not crud.get_strain(db, strain_id=strain_id):
        raise HTTPException(status_code=404, detail="La cepa especificada no existe.")
    validate_file_extension_for_analysis_type(file.filename, 'fasta')
    object_key = f"uploads/{uuid.uuid4()}-{file.filename}"

    try:
        s3_client.upload_fileobj(file.file, S3_BUCKET_NAME, object_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir el archivo a MinIO: {e}")

    first_user = db.query(models.User).first()
    if not first_user:
        raise HTTPException(status_code=500, detail="No hay usuarios en la base de datos para asociar el análisis.")

    task = process_fasta_gc_content.delay(
        strain_id=strain_id,
        owner_id=first_user.id,
        bucket=S3_BUCKET_NAME,
        object_key=object_key,
        analysis_type_str="fasta_gc_content"
    )
    return {"message": "Análisis de contenido GC FASTA iniciado", "task_id": task.id}

@router.post("/upload/fastq_stats", status_code=status.HTTP_202_ACCEPTED)
async def upload_and_analyze_fastq(
    strain_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    s3_client = Depends(get_s3_client)  # <-- INJECTED DEPENDENCY
):
    """
    Endpoint para subir un archivo FASTQ y calcular estadísticas de calidad.
    """
    if not crud.get_strain(db, strain_id=strain_id):
        raise HTTPException(status_code=404, detail="La cepa especificada no existe.")
    validate_file_extension_for_analysis_type(file.filename, 'fastq')
    object_key = f"uploads/{uuid.uuid4()}-{file.filename}"

    try:
        s3_client.upload_fileobj(file.file, S3_BUCKET_NAME, object_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir el archivo a MinIO: {e}")

    first_user = db.query(models.User).first()
    if not first_user:
        raise HTTPException(status_code=500, detail="No hay usuarios en la base de datos para asociar el análisis.")

    task = process_fastq_stats.delay(
        strain_id=strain_id,
        owner_id=first_user.id,
        bucket=S3_BUCKET_NAME,
        object_key=object_key,
        analysis_type_str="fastq_stats"
    )
    return {"message": "Análisis de estadísticas FASTQ iniciado", "task_id": task.id}

@router.post("/upload/genbank_stats", status_code=status.HTTP_202_ACCEPTED)
async def upload_and_analyze_genbank(
    strain_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    s3_client = Depends(get_s3_client)  # <-- INJECTED DEPENDENCY
):
    """
    Endpoint para subir un archivo GenBank y extraer estadísticas y anotaciones.
    """
    if not crud.get_strain(db, strain_id=strain_id):
        raise HTTPException(status_code=404, detail="La cepa especificada no existe.")
    validate_file_extension_for_analysis_type(file.filename, 'genbank')
    object_key = f"uploads/{uuid.uuid4()}-{file.filename}"

    try:
        s3_client.upload_fileobj(file.file, S3_BUCKET_NAME, object_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir el archivo a MinIO: {e}")

    first_user = db.query(models.User).first()
    if not first_user:
        raise HTTPException(status_code=500, detail="No hay usuarios en la base de datos para asociar el análisis.")

    task = process_genbank_stats.delay(
        strain_id=strain_id,
        owner_id=first_user.id,
        bucket=S3_BUCKET_NAME,
        object_key=object_key,
        analysis_type_str="genbank_stats"
    )
    return {"message": "Análisis de estadísticas GenBank iniciado", "task_id": task.id}

@router.post("/upload/gff_stats", status_code=status.HTTP_202_ACCEPTED)
async def upload_and_analyze_gff(
    strain_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    s3_client = Depends(get_s3_client)  # <-- INJECTED DEPENDENCY
):
    """
    Endpoint para subir un archivo GFF y contar los tipos de features.
    """
    if not crud.get_strain(db, strain_id=strain_id):
        raise HTTPException(status_code=404, detail="La cepa especificada no existe.")
    validate_file_extension_for_analysis_type(file.filename, 'gff')
    object_key = f"uploads/{uuid.uuid4()}-{file.filename}"

    try:
        s3_client.upload_fileobj(file.file, S3_BUCKET_NAME, object_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir el archivo a MinIO: {e}")

    first_user = db.query(models.User).first()
    if not first_user:
        raise HTTPException(status_code=500, detail="No hay usuarios en la base de datos para asociar el análisis.")

    task = process_gff_stats.delay(
        strain_id=strain_id,
        owner_id=first_user.id,
        bucket=S3_BUCKET_NAME,
        object_key=object_key,
        analysis_type_str="gff_stats"
    )
    return {"message": "Análisis de estadísticas GFF iniciado", "task_id": task.id}


def _format_results_to_text(analysis: models.Analysis) -> str:
    """
    Helper function to format analysis results from JSON into a human-readable string.
    """
    if not analysis.results or not isinstance(analysis.results, dict):
        return "No hay resultados disponibles para este análisis."

    # Start building the text content
    lines = []
    lines.append("=======================================")
    lines.append("      Resultados del Análisis")
    lines.append("=======================================")
    lines.append(f"ID de Análisis: {analysis.id}")
    lines.append(f"Tipo de Análisis: {analysis.analysis_type}")
    lines.append(f"Fecha: {analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("---------------------------------------")
    lines.append("Resultados:")

    for key, value in analysis.results.items():
        lines.append(f"  - {key}: {value}")

    lines.append("=======================================")

    return "\n".join(lines)


@router.get("/{analysis_id}/results/download-txt")
def download_analysis_results_as_txt(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """
    Downloads the results of a specific analysis as a .txt file.
    """
    # Fetch the analysis from the database
    analysis = crud.get_analysis(db, analysis_id=analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado.")

    # Format the results into a text string
    text_content = _format_results_to_text(analysis)

    # Define headers for file download
    headers = {
        'Content-Disposition': f'attachment; filename="analysis_results_{analysis_id}.txt"'
    }

    # Return a Response object with the text content and headers
    # Need to import Response from fastapi
    return Response(content=text_content, media_type="text/plain", headers=headers)


@router.get("/user/{user_id}/recent-analyses", response_model=List[schemas.Analysis])
def get_recent_analyses_for_user(
    user_id: int,
    limit: int = 10,  # Valor por defecto de 10 análisis recientes
    db: Session = Depends(get_db)
):
    """
    Devuelve una lista de los análisis más recientes para un usuario específico.
    """
    # Verificar si el usuario existe
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # Obtener los análisis recientes para este usuario
    analyses = crud.get_analyses(db, skip=0, limit=limit)

    # Filtrar para que solo devuelva análisis del usuario especificado
    user_analyses = [analysis for analysis in analyses if analysis.owner_id == user_id]

    return user_analyses

@router.get("/{analysis_id}/download")
def download_analysis_file(
    analysis_id: int,
    db: Session = Depends(get_db),
    s3_client = Depends(get_s3_client)
):
    """
    Downloads the original file associated with a specific analysis from MinIO.
    """
    # Fetch the analysis from the database
    analysis = crud.get_analysis(db, analysis_id=analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado.")

    # Extract bucket and object key from the stored file_url
    if not analysis.file_url:
        raise HTTPException(status_code=404, detail="No se encontró la URL del archivo asociado al análisis.")

    try:
        # Parse the file URL to extract bucket and object key
        # URL format: http://minio:9000/genolab-bucket/uploads/some-uuid-filename.fasta
        url_parts = analysis.file_url.split('/')
        if len(url_parts) < 5:  # Expected format: [protocol, '', host, bucket, key...]
            raise HTTPException(status_code=500, detail="Formato de URL de archivo inválido.")

        bucket_name = url_parts[3]  # Typically 'genolab-bucket'
        object_key = '/'.join(url_parts[4:])  # Everything after the bucket name

        # Get the file from MinIO
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)

        # Get the file content
        file_content = response['Body'].read()

        # Extract original filename from object key
        original_filename = object_key.split('/')[-1]

        # Define headers for file download
        headers = {
            'Content-Disposition': f'attachment; filename="{original_filename}"',
            'Content-Type': 'application/octet-stream'
        }

        # Return the file content as a response
        return Response(content=file_content, headers=headers)

    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="El archivo no se encuentra en MinIO.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar el archivo: {str(e)}")
