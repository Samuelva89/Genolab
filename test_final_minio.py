"""
Prueba final de subida de archivos a MinIO usando cepas existentes
"""
import requests
import json
from pathlib import Path

# Configura la URL base del backend
BASE_URL = "http://localhost:8000"

def test_file_upload(file_path, strain_id):
    """Subir un archivo específico"""
    try:
        with open(file_path, 'rb') as f:
            files = {"file": (file_path.name, f, "text/plain")}
            data = {"strain_id": str(strain_id), "analysis_type": "raw_file"}

            print(f"Intentando subir {file_path.name} a la cepa {strain_id}...")
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
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=== Prueba final de subida de archivos a MinIO ===\n")

    # Usar cepa existente (ID 1 basado en la salida anterior)
    strain_id = 1
    print(f"Usando cepa existente con ID: {strain_id}")

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
    print("Si viste archivos subidos exitosamente, la funcionalidad de MinIO está funcionando correctamente!")

if __name__ == "__main__":
    main()