"""
Pruebas para endpoints de análisis genómicos
"""
import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from app.main import app
from app.database import Base, get_db
from app import models, schemas, crud

# Configurar base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

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

    # Crear un usuario de prueba
    user_data = {
        "email": "test@example.com",
        "name": "Test User"
    }
    response = client.post("/api/ceparium/users/", json=user_data)
    user = response.json()

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

    yield {"user": user, "organism": organism, "strain": strain}

    # Limpiar: eliminar tablas después de las pruebas
    Base.metadata.drop_all(bind=engine)


def test_fasta_count_analysis(setup_test_db):
    """Prueba para análisis de conteo FASTA"""
    strain_id = setup_test_db["strain"]["id"]

    # Crear archivo FASTA de prueba
    fasta_content = """>Sequence1
ATGCGATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
>Sequence2
ATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
>Sequence3
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

    assert response.status_code == 202
    assert "task_id" in response.json()

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_fasta_gc_content_analysis(setup_test_db):
    """Prueba para análisis de contenido GC FASTA"""
    strain_id = setup_test_db["strain"]["id"]

    # Crear archivo FASTA de prueba con contenido GC conocido
    fasta_content = """>Sequence1
ATGCGATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
>Sequence2
GGGGGGGGGGG
CCCCCCCCCCC
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as temp_file:
        temp_file.write(fasta_content)
        temp_file_path = temp_file.name

    with open(temp_file_path, 'rb') as f:
        response = client.post(
            "/api/analysis/upload/fasta_gc_content",
            data={"strain_id": str(strain_id)},
            files={"file": ("test.fasta", f, "text/plain")}
        )

    assert response.status_code == 202
    assert "task_id" in response.json()

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_fastq_stats_analysis(setup_test_db):
    """Prueba para análisis de estadísticas FASTQ"""
    strain_id = setup_test_db["strain"]["id"]

    # Crear archivo FASTQ de prueba
    fastq_content = """@Sequence1
ATGCGATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
+
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
@Sequence2
ATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
+
HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fastq', delete=False) as temp_file:
        temp_file.write(fastq_content)
        temp_file_path = temp_file.name

    with open(temp_file_path, 'rb') as f:
        response = client.post(
            "/api/analysis/upload/fastq_stats",
            data={"strain_id": str(strain_id)},
            files={"file": ("test.fastq", f, "text/plain")}
        )

    assert response.status_code == 202
    assert "task_id" in response.json()

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_genbank_stats_analysis(setup_test_db):
    """Prueba para análisis de estadísticas GenBank"""
    strain_id = setup_test_db["strain"]["id"]

    # Crear archivo GenBank de prueba (simplificado)
    genbank_content = """LOCUS       TestSeq     1000 bp    DNA     linear   UNK
DEFINITION  Test sequence.
ACCESSION   TestSeq
VERSION     TestSeq.1
KEYWORDS    .
SOURCE      Saccharomyces cerevisiae
  ORGANISM  Saccharomyces cerevisiae
            Eukaryota; Fungi; Ascomycetes.
FEATURES             Location/Qualifiers
     source          1..1000
                     /organism="Saccharomyces cerevisiae"
                     /mol_type="genomic DNA"
ORIGIN      
        1 atgCGATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
       61 atgCGATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
//
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gb', delete=False) as temp_file:
        temp_file.write(genbank_content)
        temp_file_path = temp_file.name

    with open(temp_file_path, 'rb') as f:
        response = client.post(
            "/api/analysis/upload/genbank_stats",
            data={"strain_id": str(strain_id)},
            files={"file": ("test.gb", f, "text/plain")}
        )

    assert response.status_code == 202
    assert "task_id" in response.json()

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_gff_stats_analysis(setup_test_db):
    """Prueba para análisis de estadísticas GFF"""
    strain_id = setup_test_db["strain"]["id"]

    # Crear archivo GFF de prueba
    gff_content = """##gff-version 3
##sequence-region NC_000001 1 247249719
NC_000001\tEnsembl\tgene\t11869\t14409\t.\t+\t.\tgene_id=ENSG00000223972;gene_name=DDX11L1;gene_source=ensembl_havana
NC_000001\tEnsembl\ttranscript\t11869\t14409\t.\t+\t.\tgene_id=ENSG00000223972;transcript_id=ENST00000456328;gene_name=DDX11L1
NC_000001\tEnsembl\texon\t11869\t12227\t.\t+\t.\tgene_id=ENSG00000223972;transcript_id=ENST00000456328;exon_number=1
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gff', delete=False) as temp_file:
        temp_file.write(gff_content)
        temp_file_path = temp_file.name

    with open(temp_file_path, 'rb') as f:
        response = client.post(
            "/api/analysis/upload/gff_stats",
            data={"strain_id": str(strain_id)},
            files={"file": ("test.gff", f, "text/plain")}
        )

    assert response.status_code == 202
    assert "task_id" in response.json()

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_raw_file_upload(setup_test_db):
    """Prueba para subida de archivos sin análisis"""
    strain_id = setup_test_db["strain"]["id"]

    # Crear archivo FASTA de prueba para subida directa
    fasta_content = """>Sequence1
ATGCGATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
>Sequence2
ATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
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

    assert response.status_code == 201
    response_data = response.json()
    assert "analysis_id" in response_data
    assert "file_url" in response_data

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_get_analysis_by_strain(setup_test_db):
    """Prueba para obtener análisis asociados a una cepa"""
    strain_id = setup_test_db["strain"]["id"]

    response = client.get(f"/api/analysis/strain/{strain_id}")
    
    # Puede devolver 200 (con análisis) o 204 (sin análisis), dependiendo de si otros tests se ejecutaron
    assert response.status_code in [200, 204]