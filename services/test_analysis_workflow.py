"""
Pruebas para flujo completo de análisis
"""
import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app import models, crud

# Configurar base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_workflow.db"

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
def setup_workflow_db():
    """Configurar la base de datos para pruebas de flujo"""
    Base.metadata.create_all(bind=engine)

    # Crear un organismo de prueba
    organism_data = {
        "name": "Escherichia coli",
        "genus": "Escherichia",
        "species": "coli"
    }
    response = client.post("/api/ceparium/organisms/", json=organism_data)
    organism = response.json()

    # Crear una cepa de prueba
    strain_data = {
        "strain_name": "DH5α",
        "source": "Lab strain",
        "organism_id": organism["id"]
    }
    response = client.post("/api/ceparium/strains/", json=strain_data)
    strain = response.json()

    yield {"organism": organism, "strain": strain}

    Base.metadata.drop_all(bind=engine)


def test_complete_fasta_analysis_workflow(setup_workflow_db):
    """Prueba de extremo a extremo para análisis FASTA"""
    strain_id = setup_workflow_db["strain"]["id"]

    # 1. Subir archivo FASTA para conteo
    fasta_content = """>seq1
ATGCGATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
>seq2
ATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
>seq3
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
    response_data = response.json()
    assert "task_id" in response_data

    task_id = response_data["task_id"]

    # 2. Verificar estado de la tarea
    status_response = client.get(f"/api/analysis/tasks/{task_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert "state" in status_data

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_complete_fasta_gc_analysis_workflow(setup_workflow_db):
    """Prueba de extremo a extremo para análisis de contenido GC FASTA"""
    strain_id = setup_workflow_db["strain"]["id"]

    # Crear archivo FASTA de prueba
    fasta_content = """>seq1
ATGCGATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
>seq2
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
            files={"file": ("test_gc.fasta", f, "text/plain")}
        )

    assert response.status_code == 202
    response_data = response.json()
    assert "task_id" in response_data

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_complete_fastq_analysis_workflow(setup_workflow_db):
    """Prueba de extremo a extremo para análisis FASTQ"""
    strain_id = setup_workflow_db["strain"]["id"]

    # Crear archivo FASTQ de prueba
    fastq_content = """@seq1
ATGCGATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
+
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
@seq2
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
    response_data = response.json()
    assert "task_id" in response_data

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_complete_genbank_analysis_workflow(setup_workflow_db):
    """Prueba de extremo a extremo para análisis GenBank"""
    strain_id = setup_workflow_db["strain"]["id"]

    # Crear archivo GenBank de prueba
    genbank_content = """LOCUS       TestSeq     1000 bp    DNA     linear   UNK
DEFINITION  Test sequence.
ACCESSION   TestSeq
VERSION     TestSeq.1
KEYWORDS    .
SOURCE      Escherichia coli
  ORGANISM  Escherichia coli
            Bacteria; Proteobacteria; Gammaproteobacteria.
FEATURES             Location/Qualifiers
     source          1..1000
                     /organism="Escherichia coli"
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
    response_data = response.json()
    assert "task_id" in response_data

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_complete_gff_analysis_workflow(setup_workflow_db):
    """Prueba de extremo a extremo para análisis GFF"""
    strain_id = setup_workflow_db["strain"]["id"]

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
    response_data = response.json()
    assert "task_id" in response_data

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_raw_file_upload_and_retrieval(setup_workflow_db):
    """Prueba para subida directa de archivos y verificación"""
    strain_id = setup_workflow_db["strain"]["id"]

    # Crear archivo FASTA para subida directa
    fasta_content = """>TestSequence
ATGCGATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as temp_file:
        temp_file.write(fasta_content)
        temp_file_path = temp_file.name

    with open(temp_file_path, 'rb') as f:
        response = client.post(
            "/api/analysis/upload/raw",
            data={"strain_id": str(strain_id), "analysis_type": "raw_file"},
            files={"file": ("test_raw.fasta", f, "text/plain")}
        )

    assert response.status_code == 201
    response_data = response.json()
    assert "analysis_id" in response_data
    assert "file_url" in response_data

    # Verificar que el análisis se registró correctamente
    analysis_id = response_data["analysis_id"]
    
    # Obtener análisis por ID
    analysis_response = client.get(f"/api/analysis/strain/{strain_id}")
    assert analysis_response.status_code == 200
    analyses = analysis_response.json()
    
    # Verificar que el análisis subido está en la lista
    raw_analysis = None
    for analysis in analyses:
        if analysis["id"] == analysis_id:
            raw_analysis = analysis
            break
    
    assert raw_analysis is not None
    assert raw_analysis["analysis_type"] == "raw_file"
    assert raw_analysis["results"]["upload_status"] == "completed"

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_multiple_file_types_upload(setup_workflow_db):
    """Prueba para subida de múltiples tipos de archivos diferentes"""
    strain_id = setup_workflow_db["strain"]["id"]

    # Subir archivo FASTA
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as temp_fasta:
        temp_fasta.write(""">seq1
ATGCGATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
""")
        temp_fasta_path = temp_fasta.name

    with open(temp_fasta_path, 'rb') as f:
        response = client.post(
            "/api/analysis/upload/raw",
            data={"strain_id": str(strain_id), "analysis_type": "raw_file"},
            files={"file": ("test.fasta", f, "text/plain")}
        )
    
    assert response.status_code == 201

    # Subir archivo FASTQ
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fastq', delete=False) as temp_fastq:
        temp_fastq.write("""@seq1
ATGCGATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
+
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
""")
        temp_fastq_path = temp_fastq.name

    with open(temp_fastq_path, 'rb') as f:
        response = client.post(
            "/api/analysis/upload/raw",
            data={"strain_id": str(strain_id), "analysis_type": "raw_file"},
            files={"file": ("test.fastq", f, "text/plain")}
        )
    
    assert response.status_code == 201

    # Subir archivo GenBank
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gb', delete=False) as temp_gb:
        temp_gb.write("""LOCUS       TestSeq     1000 bp    DNA     linear   UNK
DEFINITION  Test sequence.
ACCESSION   TestSeq
VERSION     TestSeq.1
KEYWORDS    .
SOURCE      Escherichia coli
//
""")
        temp_gb_path = temp_gb.name

    with open(temp_gb_path, 'rb') as f:
        response = client.post(
            "/api/analysis/upload/raw",
            data={"strain_id": str(strain_id), "analysis_type": "raw_file"},
            files={"file": ("test.gb", f, "text/plain")}
        )
    
    assert response.status_code == 201

    # Subir archivo GFF
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gff', delete=False) as temp_gff:
        temp_gff.write("""##gff-version 3
NC_000001\tEnsembl\tgene\t11869\t14409\t.\t+\t.\tgene_id=ENSG00000223972
""")
        temp_gff_path = temp_gff.name

    with open(temp_gff_path, 'rb') as f:
        response = client.post(
            "/api/analysis/upload/raw",
            data={"strain_id": str(strain_id), "analysis_type": "raw_file"},
            files={"file": ("test.gff", f, "text/plain")}
        )
    
    assert response.status_code == 201

    # Limpiar archivos temporales
    os.unlink(temp_fasta_path)
    os.unlink(temp_fastq_path)
    os.unlink(temp_gb_path)
    os.unlink(temp_gff_path)