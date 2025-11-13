"""
Validadores para archivos subidos
"""
from fastapi import HTTPException, UploadFile, status

# Configuración de validación (idealmente desde .env)
MAX_FILE_SIZE_MB = 10  # Tamaño máximo en megabytes
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Extensiones permitidas para archivos bioinformáticos
ALLOWED_EXTENSIONS = {
    '.fasta', '.fa', '.fna', '.ffn', '.faa', '.frn',  # FASTA
    '.fastq', '.fq',  # FASTQ
    '.gb', '.gbk', '.genbank',  # GenBank
    '.gff', '.gff3',  # GFF
}

MIME_TYPES = {
    'application/octet-stream',  # Archivos binarios genéricos
    'text/plain',  # Archivos de texto
    'application/x-fasta',  # FASTA
    'application/x-fastq',  # FASTQ
}


async def validate_file_upload(
    file: UploadFile,
    allowed_extensions: set = ALLOWED_EXTENSIONS,
    max_size_bytes: int = MAX_FILE_SIZE_BYTES
) -> None:
    """
    Valida un archivo subido por tamaño y extensión.

    Args:
        file: Archivo subido
        allowed_extensions: Conjunto de extensiones permitidas
        max_size_bytes: Tamaño máximo en bytes

    Raises:
        HTTPException: Si el archivo no cumple con los requisitos
    """

    # Validar que el archivo tenga nombre
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo no tiene nombre"
        )

    # Validar extensión
    file_extension = get_file_extension(file.filename)
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extensión de archivo no permitida. Extensiones válidas: {', '.join(sorted(allowed_extensions))}"
        )

    # Validar tamaño del archivo
    contents = await file.read()
    file_size = len(contents)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo está vacío"
        )

    if file_size > max_size_bytes:
        max_size_mb = max_size_bytes / (1024 * 1024)
        current_size_mb = file_size / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Archivo demasiado grande ({current_size_mb:.2f}MB). Tamaño máximo: {max_size_mb:.0f}MB"
        )

    # Resetear el cursor del archivo para lecturas posteriores
    await file.seek(0)

    return contents


def get_file_extension(filename: str) -> str:
    """
    Obtiene la extensión del archivo en minúsculas.

    Args:
        filename: Nombre del archivo

    Returns:
        Extensión del archivo (ej: '.fasta')
    """
    if '.' not in filename:
        return ''
    return '.' + filename.rsplit('.', 1)[1].lower()


def validate_file_extension_for_analysis_type(filename: str, analysis_type: str) -> None:
    """
    Valida que la extensión del archivo coincida con el tipo de análisis.

    Args:
        filename: Nombre del archivo
        analysis_type: Tipo de análisis ('fasta', 'fastq', 'genbank', 'gff')

    Raises:
        HTTPException: Si la extensión no coincide con el tipo de análisis
    """
    extension = get_file_extension(filename)

    expected_extensions = {
        'fasta': {'.fasta', '.fa', '.fna', '.ffn', '.faa', '.frn'},
        'fastq': {'.fastq', '.fq'},
        'genbank': {'.gb', '.gbk', '.genbank'},
        'gff': {'.gff', '.gff3'},
    }

    if analysis_type in expected_extensions:
        valid_extensions = expected_extensions[analysis_type]
        if extension not in valid_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extensión de archivo '{extension}' no válida para análisis de tipo '{analysis_type}'. "
                       f"Extensiones esperadas: {', '.join(sorted(valid_extensions))}"
            )
