"""
Pruebas para tareas de análisis genómicos
"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.tasks import process_fasta_count, process_fasta_gc_content, process_fastq_stats, process_genbank_stats, process_gff_stats
from app.database import Base
from app import models

# Configurar base de datos de prueba para las tareas
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_tasks.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def setup_task_db():
    """Configurar la base de datos de prueba para tareas"""
    Base.metadata.create_all(bind=engine)

    # Crear un usuario de prueba en la base de datos
    db = TestingSessionLocal()
    user = models.User(email="test@example.com", name="Test User")
    db.add(user)
    db.commit()
    user_id = user.id
    db.close()

    yield {"user_id": user_id}

    Base.metadata.drop_all(bind=engine)


def test_process_fasta_count_task(setup_task_db):
    """Prueba para la tarea de conteo FASTA"""
    user_id = setup_task_db["user_id"]
    
    # Crear archivo FASTA de prueba
    fasta_content = """>Sequence1
ATGCGATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
>Sequence2
ATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as temp_file:
        temp_file.write(fasta_content)
        temp_file_path = temp_file.name

    # Mock del cliente S3
    with patch('app.tasks.get_s3_client') as mock_s3_client:
        mock_response = {
            'Body': type('obj', (object,), {'read': lambda: open(temp_file_path, 'rb')})
        }
        mock_s3_client.return_value.get_object.return_value = mock_response
        
        # Mock de la sesión de base de datos
        with patch('app.tasks.get_db_task') as mock_db_task:
            mock_db = MagicMock()
            mock_db_task.return_value.__iter__.return_value = [mock_db]
            
            # Mock de la función get_strain
            with patch('app.crud.get_strain') as mock_get_strain:
                mock_get_strain.return_value = type('obj', (object,), {'id': 1, 'strain_name': 'Test Strain'})
                
                # Mock de la función create_analysis
                with patch('app.crud.create_analysis') as mock_create_analysis:
                    mock_analysis = type('obj', (object,), {'id': 1})
                    mock_create_analysis.return_value = mock_analysis
                    
                    # Ejecutar la tarea
                    result = process_fasta_count(
                        strain_id=1,
                        owner_id=user_id,
                        bucket="test-bucket",
                        object_key="test.fasta",
                        analysis_type_str="fasta_count"
                    )
                    
                    assert result["status"] == "SUCCESS"
                    assert "analysis_id" in result

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_process_fasta_gc_content_task(setup_task_db):
    """Prueba para la tarea de contenido GC FASTA"""
    user_id = setup_task_db["user_id"]
    
    # Crear archivo FASTA de prueba
    fasta_content = """>Sequence1
ATGCGATCGTAGCTAGCTACGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGC
>Sequence2
GGGGGGGGGGG
CCCCCCCCCCC
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as temp_file:
        temp_file.write(fasta_content)
        temp_file_path = temp_file.name

    # Mock del cliente S3
    with patch('app.tasks.get_s3_client') as mock_s3_client:
        mock_response = {
            'Body': type('obj', (object,), {'read': lambda: open(temp_file_path, 'rb')})
        }
        mock_s3_client.return_value.get_object.return_value = mock_response
        
        # Mock de la sesión de base de datos
        with patch('app.tasks.get_db_task') as mock_db_task:
            mock_db = MagicMock()
            mock_db_task.return_value.__iter__.return_value = [mock_db]
            
            # Mock de la función get_strain
            with patch('app.crud.get_strain') as mock_get_strain:
                mock_get_strain.return_value = type('obj', (object,), {'id': 1, 'strain_name': 'Test Strain'})
                
                # Mock de la función create_analysis
                with patch('app.crud.create_analysis') as mock_create_analysis:
                    mock_analysis = type('obj', (object,), {'id': 1})
                    mock_create_analysis.return_value = mock_analysis
                    
                    # Ejecutar la tarea
                    result = process_fasta_gc_content(
                        strain_id=1,
                        owner_id=user_id,
                        bucket="test-bucket",
                        object_key="test.fasta",
                        analysis_type_str="fasta_gc_content"
                    )
                    
                    assert result["status"] == "SUCCESS"
                    assert "analysis_id" in result

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_process_fastq_stats_task(setup_task_db):
    """Prueba para la tarea de estadísticas FASTQ"""
    user_id = setup_task_db["user_id"]
    
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

    # Mock del cliente S3
    with patch('app.tasks.get_s3_client') as mock_s3_client:
        mock_response = {
            'Body': type('obj', (object,), {'read': lambda: open(temp_file_path, 'rb')})
        }
        mock_s3_client.return_value.get_object.return_value = mock_response
        
        # Mock de la sesión de base de datos
        with patch('app.tasks.get_db_task') as mock_db_task:
            mock_db = MagicMock()
            mock_db_task.return_value.__iter__.return_value = [mock_db]
            
            # Mock de la función get_strain
            with patch('app.crud.get_strain') as mock_get_strain:
                mock_get_strain.return_value = type('obj', (object,), {'id': 1, 'strain_name': 'Test Strain'})
                
                # Mock de la función create_analysis
                with patch('app.crud.create_analysis') as mock_create_analysis:
                    mock_analysis = type('obj', (object,), {'id': 1})
                    mock_create_analysis.return_value = mock_analysis
                    
                    # Ejecutar la tarea
                    result = process_fastq_stats(
                        strain_id=1,
                        owner_id=user_id,
                        bucket="test-bucket",
                        object_key="test.fastq",
                        analysis_type_str="fastq_stats"
                    )
                    
                    assert result["status"] == "SUCCESS"
                    assert "analysis_id" in result

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_process_genbank_stats_task(setup_task_db):
    """Prueba para la tarea de estadísticas GenBank"""
    user_id = setup_task_db["user_id"]
    
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

    # Mock del cliente S3
    with patch('app.tasks.get_s3_client') as mock_s3_client:
        mock_response = {
            'Body': type('obj', (object,), {'read': lambda: open(temp_file_path, 'rb')})
        }
        mock_s3_client.return_value.get_object.return_value = mock_response
        
        # Mock de la sesión de base de datos
        with patch('app.tasks.get_db_task') as mock_db_task:
            mock_db = MagicMock()
            mock_db_task.return_value.__iter__.return_value = [mock_db]
            
            # Mock de la función get_strain
            with patch('app.crud.get_strain') as mock_get_strain:
                mock_get_strain.return_value = type('obj', (object,), {'id': 1, 'strain_name': 'Test Strain'})
                
                # Mock de la función create_analysis
                with patch('app.crud.create_analysis') as mock_create_analysis:
                    mock_analysis = type('obj', (object,), {'id': 1})
                    mock_create_analysis.return_value = mock_analysis
                    
                    # Ejecutar la tarea
                    result = process_genbank_stats(
                        strain_id=1,
                        owner_id=user_id,
                        bucket="test-bucket",
                        object_key="test.gb",
                        analysis_type_str="genbank_stats"
                    )
                    
                    assert result["status"] == "SUCCESS"
                    assert "analysis_id" in result

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_process_gff_stats_task(setup_task_db):
    """Prueba para la tarea de estadísticas GFF"""
    user_id = setup_task_db["user_id"]
    
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

    # Mock del cliente S3
    with patch('app.tasks.get_s3_client') as mock_s3_client:
        mock_response = {
            'Body': type('obj', (object,), {'read': lambda: open(temp_file_path, 'rb')})
        }
        mock_s3_client.return_value.get_object.return_value = mock_response
        
        # Mock de la sesión de base de datos
        with patch('app.tasks.get_db_task') as mock_db_task:
            mock_db = MagicMock()
            mock_db_task.return_value.__iter__.return_value = [mock_db]
            
            # Mock de la función get_strain
            with patch('app.crud.get_strain') as mock_get_strain:
                mock_get_strain.return_value = type('obj', (object,), {'id': 1, 'strain_name': 'Test Strain'})
                
                # Mock de la función create_analysis
                with patch('app.crud.create_analysis') as mock_create_analysis:
                    mock_analysis = type('obj', (object,), {'id': 1})
                    mock_create_analysis.return_value = mock_analysis
                    
                    # Ejecutar la tarea
                    result = process_gff_stats(
                        strain_id=1,
                        owner_id=user_id,
                        bucket="test-bucket",
                        object_key="test.gff",
                        analysis_type_str="gff_stats"
                    )
                    
                    assert result["status"] == "SUCCESS"
                    assert "analysis_id" in result

    # Limpiar archivo temporal
    os.unlink(temp_file_path)


def test_task_error_handling():
    """Prueba para manejo de errores en tareas"""
    # Mock del cliente S3 para fallar
    with patch('app.tasks.get_s3_client') as mock_s3_client:
        mock_s3_client.side_effect = Exception("Error al conectarse a S3")
        
        # Mock de la sesión de base de datos
        with patch('app.tasks.get_db_task') as mock_db_task:
            mock_db = MagicMock()
            mock_db_task.return_value.__iter__.return_value = [mock_db]
            
            # Mock de la sesión secundaria para manejo de errores
            with patch('app.tasks.SessionLocal') as mock_session_local:
                error_db = MagicMock()
                mock_session_local.return_value.__enter__.return_value = error_db
                mock_session_local.return_value.__exit__.return_value = None
                
                # Ejecutar la tarea (debería fallar)
                result = process_fasta_count(
                    strain_id=1,
                    owner_id=1,
                    bucket="test-bucket",
                    object_key="nonexistent.fasta",
                    analysis_type_str="fasta_count"
                )
                
                assert result["status"] == "FAILED"
                assert "error" in result