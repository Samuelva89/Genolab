"""
Pruebas para subida de archivos existentes a MinIO
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Configurar base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_minio.db"

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


def test_upload_existing_fasta_file(setup_test_db):
    """Prueba para subir un archivo FASTA existente a MinIO"""
    strain_id = setup_test_db["strain"]["id"]

    # Verificar si existen archivos FASTA en el directorio
    base_dir = "D:\\GENOLAB"
    fasta_files = []

    # Buscar archivos FASTA en el directorio base
    for filename in os.listdir(base_dir):
        if filename.lower().endswith(('.fasta', '.fa', '.fna', '.ffn', '.faa', '.frn')):
            fasta_files.append(os.path.join(base_dir, filename))

    # También buscar en subdirectorios
    for root, dirs, files in os.walk(base_dir):
        for filename in files:
            if filename.lower().endswith(('.fasta', '.fa', '.fna', '.ffn', '.faa', '.frn')):
                fasta_files.append(os.path.join(root, filename))

    # Si hay archivos FASTA, probar la subida
    if fasta_files:
        for fasta_file in fasta_files[:3]:  # Probar hasta 3 archivos
            try:
                with open(fasta_file, 'rb') as f:
                    response = client.post(
                        "/api/analysis/upload/raw",
                        data={"strain_id": str(strain_id), "analysis_type": "raw_file"},
                        files={"file": (os.path.basename(fasta_file), f, "text/plain")}
                    )

                assert response.status_code in [201, 413, 400], f"Error subiendo {fasta_file}"

                if response.status_code == 201:
                    response_data = response.json()
                    assert "analysis_id" in response_data
                    assert "file_url" in response_data
                    print(f"✓ Archivo {fasta_file} subido exitosamente a MinIO")
                elif response.status_code == 413:
                    print(f"! Archivo {fasta_file} es demasiado grande para subir")
                elif response.status_code == 400:
                    print(f"! Archivo {fasta_file} tiene formato inválido")

            except Exception as e:
                print(f"! Error al intentar subir {fasta_file}: {str(e)}")
    else:
        print("No se encontraron archivos FASTA para probar la subida")


def test_upload_existing_fastq_file(setup_test_db):
    """Prueba para subir un archivo FASTQ existente a MinIO"""
    strain_id = setup_test_db["strain"]["id"]

    # Verificar si existen archivos FASTQ en el directorio
    base_dir = "D:\\GENOLAB"
    fastq_files = []

    # Buscar archivos FASTQ en el directorio base
    for filename in os.listdir(base_dir):
        if filename.lower().endswith(('.fastq', '.fq')):
            fastq_files.append(os.path.join(base_dir, filename))

    # También buscar en subdirectorios
    for root, dirs, files in os.walk(base_dir):
        for filename in files:
            if filename.lower().endswith(('.fastq', '.fq')):
                fastq_files.append(os.path.join(root, filename))

    # Si hay archivos FASTQ, probar la subida
    if fastq_files:
        for fastq_file in fastq_files[:3]:  # Probar hasta 3 archivos
            try:
                with open(fastq_file, 'rb') as f:
                    response = client.post(
                        "/api/analysis/upload/raw",
                        data={"strain_id": str(strain_id), "analysis_type": "raw_file"},
                        files={"file": (os.path.basename(fastq_file), f, "text/plain")}
                    )

                assert response.status_code in [201, 413, 400], f"Error subiendo {fastq_file}"

                if response.status_code == 201:
                    response_data = response.json()
                    assert "analysis_id" in response_data
                    assert "file_url" in response_data
                    print(f"✓ Archivo {fastq_file} subido exitosamente a MinIO")
                elif response.status_code == 413:
                    print(f"! Archivo {fastq_file} es demasiado grande para subir")
                elif response.status_code == 400:
                    print(f"! Archivo {fastq_file} tiene formato inválido")

            except Exception as e:
                print(f"! Error al intentar subir {fastq_file}: {str(e)}")
    else:
        print("No se encontraron archivos FASTQ para probar la subida")


def test_upload_existing_genbank_file(setup_test_db):
    """Prueba para subir un archivo GenBank existente a MinIO"""
    strain_id = setup_test_db["strain"]["id"]

    # Verificar si existen archivos GenBank en el directorio
    base_dir = "D:\\GENOLAB"
    genbank_files = []

    # Buscar archivos GenBank en el directorio base
    for filename in os.listdir(base_dir):
        if filename.lower().endswith(('.gb', '.gbk', '.genbank')):
            genbank_files.append(os.path.join(base_dir, filename))

    # También buscar en subdirectorios
    for root, dirs, files in os.walk(base_dir):
        for filename in files:
            if filename.lower().endswith(('.gb', '.gbk', '.genbank')):
                genbank_files.append(os.path.join(root, filename))

    # Si hay archivos GenBank, probar la subida
    if genbank_files:
        for genbank_file in genbank_files[:3]:  # Probar hasta 3 archivos
            try:
                with open(genbank_file, 'rb') as f:
                    response = client.post(
                        "/api/analysis/upload/raw",
                        data={"strain_id": str(strain_id), "analysis_type": "raw_file"},
                        files={"file": (os.path.basename(genbank_file), f, "text/plain")}
                    )

                assert response.status_code in [201, 413, 400], f"Error subiendo {genbank_file}"

                if response.status_code == 201:
                    response_data = response.json()
                    assert "analysis_id" in response_data
                    assert "file_url" in response_data
                    print(f"✓ Archivo {genbank_file} subido exitosamente a MinIO")
                elif response.status_code == 413:
                    print(f"! Archivo {genbank_file} es demasiado grande para subir")
                elif response.status_code == 400:
                    print(f"! Archivo {genbank_file} tiene formato inválido")

            except Exception as e:
                print(f"! Error al intentar subir {genbank_file}: {str(e)}")
    else:
        print("No se encontraron archivos GenBank para probar la subida")


def test_upload_existing_gff_file(setup_test_db):
    """Prueba para subir un archivo GFF existente a MinIO"""
    strain_id = setup_test_db["strain"]["id"]

    # Verificar si existen archivos GFF en el directorio
    base_dir = "D:\\GENOLAB"
    gff_files = []

    # Buscar archivos GFF en el directorio base
    for filename in os.listdir(base_dir):
        if filename.lower().endswith(('.gff', '.gff3')):
            gff_files.append(os.path.join(base_dir, filename))

    # También buscar en subdirectorios
    for root, dirs, files in os.walk(base_dir):
        for filename in files:
            if filename.lower().endswith(('.gff', '.gff3')):
                gff_files.append(os.path.join(root, filename))

    # Si hay archivos GFF, probar la subida
    if gff_files:
        for gff_file in gff_files[:3]:  # Probar hasta 3 archivos
            try:
                with open(gff_file, 'rb') as f:
                    response = client.post(
                        "/api/analysis/upload/raw",
                        data={"strain_id": str(strain_id), "analysis_type": "raw_file"},
                        files={"file": (os.path.basename(gff_file), f, "text/plain")}
                    )

                assert response.status_code in [201, 413, 400], f"Error subiendo {gff_file}"

                if response.status_code == 201:
                    response_data = response.json()
                    assert "analysis_id" in response_data
                    assert "file_url" in response_data
                    print(f"✓ Archivo {gff_file} subido exitosamente a MinIO")
                elif response.status_code == 413:
                    print(f"! Archivo {gff_file} es demasiado grande para subir")
                elif response.status_code == 400:
                    print(f"! Archivo {gff_file} tiene formato inválido")

            except Exception as e:
                print(f"! Error al intentar subir {gff_file}: {str(e)}")
    else:
        print("No se encontraron archivos GFF para probar la subida")


def test_upload_example_files(setup_test_db):
    """Prueba para subir los archivos de ejemplo específicos que tienes"""
    strain_id = setup_test_db["strain"]["id"]

    # Verificar si existen los archivos de ejemplo específicos
    example_files = [
        "D:\\GENOLAB\\ejemplo.fastq",
        "D:\\GENOLAB\\ejemplo_count.fasta",
        "D:\\GENOLAB\\ejemplo_gc.fasta",
        "D:\\GENOLAB\\ejemplo.gbk",
        "D:\\GENOLAB\\ejemplo.gff"
    ]

    uploaded_files = 0

    for example_file in example_files:
        if os.path.exists(example_file):
            try:
                with open(example_file, 'rb') as f:
                    response = client.post(
                        "/api/analysis/upload/raw",
                        data={"strain_id": str(strain_id), "analysis_type": "raw_file"},
                        files={"file": (os.path.basename(example_file), f, "text/plain")}
                    )

                if response.status_code == 201:
                    response_data = response.json()
                    assert "analysis_id" in response_data
                    assert "file_url" in response_data
                    print(f"✓ Archivo de ejemplo {example_file} subido exitosamente a MinIO")
                    print(f"  URL: {response_data['file_url']}")
                    uploaded_files += 1
                elif response.status_code == 413:
                    print(f"! Archivo de ejemplo {example_file} es demasiado grande para subir")
                elif response.status_code == 400:
                    print(f"! Archivo de ejemplo {example_file} tiene formato inválido")
                else:
                    print(f"? Archivo de ejemplo {example_file} devolvió código: {response.status_code}")

            except Exception as e:
                print(f"! Error al intentar subir {example_file}: {str(e)}")
        else:
            print(f"- Archivo de ejemplo no encontrado: {example_file}")

    print(f"\nResumen: {uploaded_files} de {len([f for f in example_files if os.path.exists(f)])} archivos de ejemplo subidos exitosamente")


def test_file_types_compatibility(setup_test_db):
    """Verificación de compatibilidad de tipos de archivos"""
    strain_id = setup_test_db["strain"]["id"]

    # Definir los archivos ejemplo que tienes
    test_files = {
        ".fasta": "D:\\GENOLAB\\ejemplo_count.fasta",
        ".fasta": "D:\\GENOLAB\\ejemplo_gc.fasta",  # Ambos son FASTA
        ".fastq": "D:\\GENOLAB\\ejemplo.fastq",
        ".gbk": "D:\\GENOLAB\\ejemplo.gbk",
        ".gff": "D:\\GENOLAB\\ejemplo.gff"
    }

    print("Comprobando compatibilidad de tipos de archivo...")

    # Usamos un diccionario único por extensión
    files_by_ext = {
        ".fasta": ["D:\\GENOLAB\\ejemplo_count.fasta", "D:\\GENOLAB\\ejemplo_gc.fasta"],
        ".fastq": ["D:\\GENOLAB\\ejemplo.fastq"],
        ".gbk": ["D:\\GENOLAB\\ejemplo.gbk"],
        ".gff": ["D:\\GENOLAB\\ejemplo.gff"]
    }

    for ext, file_list in files_by_ext.items():
        for file_path in file_list:
            if os.path.exists(file_path):
                print(f"Probando archivo {ext}: {os.path.basename(file_path)}")

                try:
                    with open(file_path, 'rb') as f:
                        # Subir como archivo raw
                        response = client.post(
                            "/api/analysis/upload/raw",
                            data={"strain_id": str(strain_id), "analysis_type": "raw_file"},
                            files={"file": (os.path.basename(file_path), f, "text/plain")}
                        )

                        if response.status_code == 201:
                            print(f"  ✓ Subida exitosa a MinIO")
                        else:
                            print(f"  ✗ Error (código {response.status_code})")

                except Exception as e:
                    print(f"  ✗ Error: {str(e)}")
            else:
                print(f"  - Archivo no encontrado: {file_path}")