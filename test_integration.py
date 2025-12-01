"""
Script para ejecutar pruebas de integración con el backend real
"""
import os
import sys
import requests
import json
from pathlib import Path

# Asegurarnos de que el backend esté corriendo
BASE_URL = os.getenv('API_URL', 'http://localhost:8000')

def check_backend_health():
    """Verificar si el backend está disponible"""
    try:
        response = requests.get(f"{BASE_URL}/")
        return response.status_code == 200
    except:
        return False

def create_test_strain():
    """Crear una cepa de prueba para las subidas"""
    try:
        # Crear organismo de prueba
        organism_data = {
            "name": "Prueba Organismo",
            "genus": "Test",
            "species": "test"
        }
        response = requests.post(f"{BASE_URL}/api/ceparium/organisms/", json=organism_data)
        if response.status_code != 200:
            print(f"Error creando organismo: {response.status_code}")
            return None

        organism = response.json()

        # Crear cepa de prueba
        strain_data = {
            "strain_name": "Cepa de Prueba",
            "source": "Prueba de integración",
            "organism_id": organism["id"]
        }
        response = requests.post(f"{BASE_URL}/api/ceparium/strains/", json=strain_data)
        if response.status_code != 200:
            print(f"Error creando cepa: {response.status_code}")
            return None

        strain = response.json()
        return strain["id"]
    except Exception as e:
        print(f"Error creando cepa de prueba: {e}")
        return None

def test_file_upload(file_path, strain_id, analysis_type="raw_file"):
    """Subir un archivo específico al backend"""
    try:
        with open(file_path, 'rb') as f:
            files = {"file": f}
            data = {
                "strain_id": str(strain_id),
                "analysis_type": analysis_type
            }

            response = requests.post(
                f"{BASE_URL}/api/analysis/upload/raw",
                files=files,
                data=data
            )

        return response
    except Exception as e:
        print(f"Error subiendo archivo {file_path}: {e}")
        return None

def main():
    print("Verificando disponibilidad del backend...")
    if not check_backend_health():
        print("XXX Backend no disponible. Asegurate de que este corriendo en http://localhost:8000")
        print("Para iniciar el backend, ejecuta: uvicorn app.main:app --reload")
        return

    print("OK Backend disponible")

    print("\nCreando cepa de prueba...")
    strain_id = create_test_strain()
    if not strain_id:
        print("XXX No se pudo crear la cepa de prueba")
        return

    print(f"OK Cepa de prueba creada con ID: {strain_id}")

    # Directorio base donde estan los archivos de ejemplo
    base_dir = Path("D:/GENOLAB")
    example_files = {
        "ejemplo_count.fasta": "FASTA",
        "ejemplo_gc.fasta": "FASTA",
        "ejemplo.fastq": "FASTQ",
        "ejemplo.gbk": "GenBank",
        "ejemplo.gff": "GFF"
    }

    print(f"\nSubiendo archivos de ejemplo existentes a MinIO...\n")

    for filename, file_type in example_files.items():
        file_path = base_dir / filename
        if file_path.exists():
            print(f"Subiendo {filename} ({file_type})...")
            response = test_file_upload(file_path, strain_id)

            if response and response.status_code == 201:
                result = response.json()
                print(f"  OK Subido exitosamente a MinIO")
                print(f"     ID de analisis: {result.get('analysis_id', 'N/A')}")
                print(f"     URL: {result.get('file_url', 'N/A')}")
            elif response and response.status_code == 413:
                print(f"  XXX Archivo demasiado grande")
            elif response and response.status_code == 400:
                print(f"  XXX Formato de archivo invalido")
            else:
                print(f"  XXX Error: {response.status_code if response else 'No response'}")
        else:
            print(f"  - Archivo no encontrado: {filename}")

    # Tambien buscar otros archivos FASTA/FASTQ/GenBank/GFF en el directorio
    print(f"\nBuscando y subiendo otros archivos bioinformaticos en el directorio...")

    extensions = ['.fasta', '.fa', '.fna', '.fastq', '.fq', '.gb', '.gbk', '.gff', '.gff3']
    found_files = []

    for ext in extensions:
        found_files.extend(list(base_dir.rglob(f"*{ext}")))

    # Tomar solo los primeros 10 para no sobrecargar
    found_files = found_files[:10]

    print(f"Encontrados {len(found_files)} archivos adicionales")

    for file_path in found_files:
        if file_path.name not in example_files:  # No repetir los ejemplos
            print(f"\nSubiendo {file_path.name}...")
            response = test_file_upload(file_path, strain_id)

            if response and response.status_code == 201:
                result = response.json()
                print(f"  OK Subido exitosamente a MinIO")
                print(f"     ID de analisis: {result.get('analysis_id', 'N/A')}")
                print(f"     URL: {result.get('file_url', 'N/A')}")
            elif response and response.status_code == 413:
                print(f"  XXX Archivo demasiado grande")
            elif response and response.status_code == 400:
                print(f"  XXX Formato de archivo invalido")
            else:
                print(f"  XXX Error: {response.status_code if response else 'No response'}")

if __name__ == "__main__":
    main()