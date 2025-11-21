# Importaciones de librerías estándar y de terceros
import uuid
import boto3
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Response
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..dependencies import get_db
from ..core.config import settings
from ..core.validators import validate_file_extension_for_analysis_type
from ..tasks import process_fasta_count, process_fasta_gc_content, process_fastq_stats, process_genbank_stats, process_gff_stats # Importamos las tareas de Celery
from ..celery_worker import celery_app # Importamos la instancia de Celery para consultar el estado
from typing import List # Importar List para el tipo de retorno

# --- Configuración del Cliente MinIO/S3 ---
def get_s3_client():
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
    # Verificar si la cepa existe
    strain = crud.get_strain(db, strain_id=strain_id)
    if not strain:
        raise HTTPException(status_code=404, detail="Cepa no encontrada.")

    # Obtener los análisis para la cepa
    analyses = crud.get_analyses_by_strain(db, strain_id=strain_id)

    return analyses

@router.post("/upload/fasta_count", status_code=status.HTTP_202_ACCEPTED)
async def upload_and_count_fasta(
    strain_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Endpoint para subir un archivo FASTA y contar el número de secuencias.
    El archivo se sube a MinIO y la tarea de análisis se despacha a Celery.
    """
    # 1. Validar existencia de la cepa
    if not crud.get_strain(db, strain_id=strain_id):
        raise HTTPException(status_code=404, detail="La cepa especificada no existe.")

    # 2. Validar el archivo (puedes añadir validaciones de tamaño aquí)
    validate_file_extension_for_analysis_type(file.filename, 'fasta')

    # 3. Generar un nombre de objeto único para MinIO
    object_key = f"uploads/{uuid.uuid4()}-{file.filename}"

    # 4. Subir el archivo a MinIO
    try:
        s3_client = get_s3_client()
        s3_client.upload_fileobj(file.file, S3_BUCKET_NAME, object_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir el archivo a MinIO: {e}")

    # 5. Obtener el ID del usuario (en un sistema real, esto vendría de un token de autenticación)
    first_user = db.query(models.User).first()
    if not first_user:
        raise HTTPException(status_code=500, detail="No hay usuarios en la base de datos para asociar el análisis.")

    # 6. Despachar la tarea a Celery con la referencia al archivo en MinIO
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
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pendiente...'
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'status': task.info.get('status', 'Procesando...'),
            'progress': task.info.get('progress', 0)
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'status': 'Completado',
            'result': task.result
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'status': 'Fallido',
            'error': str(task.info)
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    return response

@router.post("/upload/fasta_gc_content", status_code=status.HTTP_202_ACCEPTED)
async def upload_and_analyze_fasta_gc_content(
    strain_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Endpoint para subir un archivo FASTA y calcular el contenido GC.
    La tarea de análisis se despacha a Celery.

    - **strain_id**: El ID de la cepa a la que se asocia este análisis.
    - **file**: El archivo en formato FASTA.
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
):
    """
    Endpoint para subir un archivo FASTQ y calcular estadísticas de calidad.
    La tarea de análisis se despacha a Celery.

    - **strain_id**: El ID de la cepa a la que se asocia este análisis.
    - **file**: El archivo en formato FASTQ.

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
):
    """
    Endpoint para subir un archivo GenBank y extraer estadísticas y anotaciones.
    La tarea de análisis se despacha a Celery.

    - **strain_id**: El ID de la cepa a la que se asocia este análisis.
    - **file**: El archivo en formato GenBank.

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
):
    """
    Endpoint para subir un archivo GFF y contar los tipos de features.
    La tarea de análisis se despacha a Celery.

    - **strain_id**: El ID de la cepa a la que se asocia este análisis.
    - **file**: El archivo en formato GFF.

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