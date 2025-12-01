"""
Pruebas para validación de archivos
"""
import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.core.validators import validate_file_extension_for_analysis_type, get_file_extension, validate_file_upload

# Configurar base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_validation.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_test_db():
    """Configurar la base de datos de prueba"""
    Base.metadata.create_all(bind=engine)

    # Crear un organismo de prueba
    organism_data = {
        "name": "Saccharomyces cerevisiae",
        "genus": "Saccharomyces",
        "species": "cerevisiae"
    }
    response = client.post("/api/ceparium/organisms/", json=organism_data)
    organism = response.json()

    # Crear una cepa de prueba
    strain_data = {
        "strain_name": "Test Strain",
        "source": "Lab collection",
        "organism_id": organism["id"]
    }
    response = client.post("/api/ceparium/strains/", json=strain_data)
    strain = response.json()

    yield {"organism": organism, "strain": strain}

    Base.metadata.drop_all(bind=engine)


def test_file_extension_validation():
    """Prueba para validación de extensiones de archivo"""
    
    # Validar extensiones correctas
    validate_file_extension_for_analysis_type("test.fasta", "fasta")
    validate_file_extension_for_analysis_type("test.fa", "fasta")
    validate_file_extension_for_analysis_type("test.fastq", "fastq")
    validate_file_extension_for_analysis_type("test.fq", "fastq")
    validate_file_extension_for_analysis_type("test.gb", "genbank")
    validate_file_extension_for_analysis_type("test.gbk", "genbank")
    validate_file_extension_for_analysis_type("test.gff", "gff")
    
    # Validar que lanza error con extensión incorrecta
    with pytest.raises(Exception):
        validate_file_extension_for_analysis_type("test.txt", "fasta")


def test_get_file_extension():
    """Prueba para obtención de extensión de archivo"""
    assert get_file_extension("test.fasta") == ".fasta"
    assert get_file_extension("test.FASTA") == ".fasta"  # Debería ser lowercase
    assert get_file_extension("path/to/test.fastq") == ".fastq"
    assert get_file_extension("test") == ""  # Sin extensión
    assert get_file_extension("") == ""  # Nombre vacío


def test_file_size_validation(setup_test_db):
    """Prueba para validación de tamaño de archivo"""
    strain_id = setup_test_db["strain"]["id"]

    # Crear archivo grande para probar validación de tamaño
    large_content = "A" * (10 * 1024 * 1024 + 1)  # Un poco más de 10MB
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as temp_file:
        temp_file.write(large_content)
        temp_file_path = temp_file.name

    with open(temp_file_path, 'rb') as f:
        response = client.post(
            "/api/analysis/upload/fasta_count",
            data={"strain_id": str(strain_id)},
            files={"file": ("large_test.fasta", f, "text/plain")}
        )

    # Debería fallar por tamaño excesivo
    assert response.status_code == 413  # Payload Too Large

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_invalid_file_extension(setup_test_db):
    """Prueba para extensión de archivo inválida"""
    strain_id = setup_test_db["strain"]["id"]

    # Crear archivo con extensión inválida
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write("contenido de prueba")
        temp_file_path = temp_file.name

    with open(temp_file_path, 'rb') as f:
        response = client.post(
            "/api/analysis/upload/fasta_count",
            data={"strain_id": str(strain_id)},
            files={"file": ("test.txt", f, "text/plain")}
        )

    # Debería fallar por extensión inválida
    assert response.status_code == 400

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_empty_file_upload(setup_test_db):
    """Prueba para subida de archivo vacío"""
    strain_id = setup_test_db["strain"]["id"]

    # Crear archivo vacío
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as temp_file:
        temp_file_path = temp_file.name

    with open(temp_file_path, 'rb') as f:
        response = client.post(
            "/api/analysis/upload/fasta_count",
            data={"strain_id": str(strain_id)},
            files={"file": ("empty.fasta", f, "text/plain")}
        )

    # Debería fallar por archivo vacío
    assert response.status_code == 400

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_valid_file_uploads(setup_test_db):
    """Prueba para subidas de archivos válidos"""
    strain_id = setup_test_db["strain"]["id"]

    # Probar subida de archivo FASTA válido
    fasta_content = """>Sequence1
ATGCGATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as temp_file:
        temp_file.write(fasta_content)
        temp_file_path = temp_file.name

    with open(temp_file_path, 'rb') as f:
        response = client.post(
            "/api/analysis/upload/fasta_count",
            data={"strain_id": str(strain_id)},
            files={"file": ("test.fasta", f, "text/plain")}
        )

    # Debería ser aceptado (202 es aceptado para procesamiento asincrónico)
    assert response.status_code == 202

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_raw_file_upload_validations(setup_test_db):
    """Prueba para validaciones en subida de archivos raw"""
    strain_id = setup_test_db["strain"]["id"]

    # Crear archivo FASTA de prueba para subida directa
    fasta_content = """>Sequence1
ATGCGATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as temp_file:
        temp_file.write(fasta_content)
        temp_file_path = temp_file.name

    with open(temp_file_path, 'rb') as f:
        response = client.post(
            "/api/analysis/upload/raw",
            data={"strain_id": str(strain_id), "analysis_type": "raw_file"},
            files={"file": ("test.fasta", f, "text/plain")}
        )

    # Debería ser aceptado (201 es creado)
    assert response.status_code == 201
    response_data = response.json()
    assert "analysis_id" in response_data
    assert "file_url" in response_data

    # Limpiar archivo temporal
    os.unlink(temp_file_path)