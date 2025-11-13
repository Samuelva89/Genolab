# Importaciones de librerías estándar y de terceros
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session

from .. import crud, models
from ..dependencies import get_db
from ..core.validators import validate_file_upload, validate_file_extension_for_analysis_type
from ..tasks import process_fasta_count, process_fasta_gc_content, process_fastq_stats, process_genbank_stats, process_gff_stats # Importamos las tareas de Celery
from ..celery_worker import celery_app # Importamos la instancia de Celery para consultar el estado
from typing import List # Importar List para el tipo de retorno
from .. import schemas # Importar schemas para el tipo de retorno

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
    La tarea de análisis se despacha a Celery.

    - **strain_id**: El ID de la cepa a la que se asocia este análisis.
    - **file**: El archivo en formato FASTA (extensiones permitidas: .fasta, .fa, .fna, etc.)
    - **Tamaño máximo:** 10MB
    """
    # Validar existencia de cepa
    if not crud.get_strain(db, strain_id=strain_id):
        raise HTTPException(status_code=404, detail="La cepa especificada no existe.")

    # Validar archivo (tamaño y extensión)
    validate_file_extension_for_analysis_type(file.filename, 'fasta')
    contents = await validate_file_upload(file)

    # Obtener el ID del primer usuario para asociar el análisis
    first_user = db.query(models.User).first()
    if not first_user:
        raise HTTPException(status_code=500, detail="No hay usuarios en la base de datos para asociar el análisis.")

    # Despachar la tarea a Celery
    task = process_fasta_count.delay(strain_id, contents, file.filename, first_user.id)

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

    contents = await file.read()
    
    # Obtener el ID del primer usuario para asociar el análisis
    first_user = db.query(models.User).first()
    if not first_user:
        raise HTTPException(status_code=500, detail="No hay usuarios en la base de datos para asociar el análisis.")

    task = process_fasta_gc_content.delay(strain_id, contents, file.filename, first_user.id)
    
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

    contents = await file.read()

    # Obtener el ID del primer usuario para asociar el análisis
    first_user = db.query(models.User).first()
    if not first_user:
        raise HTTPException(status_code=500, detail="No hay usuarios en la base de datos para asociar el análisis.")

    task = process_fastq_stats.delay(strain_id, contents, file.filename, first_user.id)

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

    contents = await file.read()

    # Obtener el ID del primer usuario para asociar el análisis
    first_user = db.query(models.User).first()
    if not first_user:
        raise HTTPException(status_code=500, detail="No hay usuarios en la base de datos para asociar el análisis.")

    task = process_genbank_stats.delay(strain_id, contents, file.filename, first_user.id)

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

    contents = await file.read()

    # Obtener el ID del primer usuario para asociar el análisis
    first_user = db.query(models.User).first()
    if not first_user:
        raise HTTPException(status_code=500, detail="No hay usuarios en la base de datos para asociar el análisis.")

    task = process_gff_stats.delay(strain_id, contents, file.filename, first_user.id)

    return {"message": "Análisis de estadísticas GFF iniciado", "task_id": task.id}