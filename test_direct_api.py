"""
Prueba directa de subida de archivos usando la API REST
"""
import requests
import json
from pathlib import Path

# Configura la URL base del backend
BASE_URL = "http://localhost:8000"

def test_api_connection():
    """Probar la conexión básica con la API"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Conexión a API: {'OK' if response.status_code == 200 else 'ERROR'}")
        if response.status_code == 200:
            print(f"Respuesta: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False

def test_organism_creation():
    """Crear un organismo de prueba"""
    try:
        organism_data = {
            "name": "Prueba API",
            "genus": "Test",
            "species": "test"
        }
        response = requests.post(f"{BASE_URL}/api/ceparium/organisms/", json=organism_data)
        print(f"Creación de organismo: {'OK' if response.status_code == 200 else 'ERROR'}")
        if response.status_code == 200:
            return response.json().get("id")
        else:
            print(f"Código de error: {response.status_code}")
            print(f"Detalle: {response.text}")
    except Exception as e:
        print(f"Error creando organismo: {e}")
    return None

def test_strain_creation(organism_id):
    """Crear una cepa de prueba"""
    try:
        strain_data = {
            "strain_name": "Cepa de prueba API",
            "source": "Prueba directa",
            "organism_id": organism_id
        }
        response = requests.post(f"{BASE_URL}/api/ceparium/strains/", json=strain_data)
        print(f"Creación de cepa: {'OK' if response.status_code == 200 else 'ERROR'}")
        if response.status_code == 200:
            return response.json().get("id")
        else:
            print(f"Código de error: {response.status_code}")
            print(f"Detalle: {response.text}")
    except Exception as e:
        print(f"Error creando cepa: {e}")
    return None

def test_file_upload(file_path, strain_id):
    """Subir un archivo específico"""
    try:
        with open(file_path, 'rb') as f:
            files = {"file": (file_path.name, f, "text/plain")}
            data = {"strain_id": str(strain_id), "analysis_type": "raw_file"}

            print(f"Intentando subir {file_path.name}...")
            response = requests.post(f"{BASE_URL}/api/analysis/upload/raw", files=files, data=data)
            print(f"Respuesta de subida: {response.status_code}")

            if response.status_code == 201:
                result = response.json()
                print(f"OK Archivo subido exitosamente a MinIO")
                print(f"ID de análisis: {result.get('analysis_id', 'N/A')}")
                print(f"URL del archivo: {result.get('file_url', 'N/A')}")
                return True
            else:
                print(f"Error en la subida: {response.status_code}")
                print(f"Detalle del error: {response.text}")
                return False
    except Exception as e:
        print(f"Error subiendo archivo: {e}")
        return False

def main():
    print("=== Prueba directa de funcionalidad de MinIO ===\n")

    # Probar conexión básica
    if not test_api_connection():
        print("\nXXX No se puede conectar a la API")
        return

    # Crear organismo
    organism_id = test_organism_creation()
    if not organism_id:
        print("\nXXX No se pudo crear organismo de prueba")
        return

    print(f"Organismo creado con ID: {organism_id}")

    # Crear cepa
    strain_id = test_strain_creation(organism_id)
    if not strain_id:
        print("\nXXX No se pudo crear cepa de prueba")
        return

    print(f"Cepa creada con ID: {strain_id}")

    # Probar subida de cada archivo de ejemplo
    base_dir = Path("D:/GENOLAB")
    example_files = ["ejemplo_count.fasta", "ejemplo_gc.fasta", "ejemplo.fastq", "ejemplo.gbk", "ejemplo.gff"]

    print(f"\n=== Subiendo archivos de ejemplo ===")
    for filename in example_files:
        file_path = base_dir / filename
        if file_path.exists():
            print(f"\nSubiendo {filename}:")
            success = test_file_upload(file_path, strain_id)
            if success:
                print(f"OK {filename} subido correctamente")
            else:
                print(f"XXX Error subiendo {filename}")
        else:
            print(f"\n- Archivo no encontrado: {filename}")

    print(f"\n=== Prueba completada ===")

if __name__ == "__main__":
    main()