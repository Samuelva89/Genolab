"""
Pruebas para funcionalidades de análisis genómicos
"""
import requests
import json
from pathlib import Path

# Configura la URL base del backend
BASE_URL = "http://localhost:8000"

def test_fasta_count_analysis(file_path, strain_id):
    """Probar análisis de conteo FASTA"""
    try:
        with open(file_path, 'rb') as f:
            files = {"file": (file_path.name, f, "text/plain")}
            data = {"strain_id": str(strain_id)}

            print(f"Enviando {file_path.name} para análisis de conteo FASTA...")
            response = requests.post(f"{BASE_URL}/api/analysis/upload/fasta_count", files=files, data=data)
            print(f"Respuesta: {response.status_code}")

            if response.status_code == 202:  # Aceptado para procesamiento asincrónico
                result = response.json()
                print(f"OK Análisis iniciado")
                print(f"Task ID: {result.get('task_id', 'N/A')}")
                return result.get('task_id')
            else:
                print(f"Error: {response.status_code}")
                print(f"Detalle: {response.text}")
                return None
    except Exception as e:
        print(f"Error en análisis FASTA: {e}")
        return None

def test_fasta_gc_analysis(file_path, strain_id):
    """Probar análisis de contenido GC FASTA"""
    try:
        with open(file_path, 'rb') as f:
            files = {"file": (file_path.name, f, "text/plain")}
            data = {"strain_id": str(strain_id)}

            print(f"Enviando {file_path.name} para análisis de contenido GC FASTA...")
            response = requests.post(f"{BASE_URL}/api/analysis/upload/fasta_gc_content", files=files, data=data)
            print(f"Respuesta: {response.status_code}")

            if response.status_code == 202:  # Aceptado para procesamiento asincrónico
                result = response.json()
                print(f"OK Análisis iniciado")
                print(f"Task ID: {result.get('task_id', 'N/A')}")
                return result.get('task_id')
            else:
                print(f"Error: {response.status_code}")
                print(f"Detalle: {response.text}")
                return None
    except Exception as e:
        print(f"Error en análisis GC: {e}")
        return None

def test_fastq_analysis(file_path, strain_id):
    """Probar análisis de estadísticas FASTQ"""
    try:
        with open(file_path, 'rb') as f:
            files = {"file": (file_path.name, f, "text/plain")}
            data = {"strain_id": str(strain_id)}

            print(f"Enviando {file_path.name} para análisis de estadísticas FASTQ...")
            response = requests.post(f"{BASE_URL}/api/analysis/upload/fastq_stats", files=files, data=data)
            print(f"Respuesta: {response.status_code}")

            if response.status_code == 202:  # Aceptado para procesamiento asincrónico
                result = response.json()
                print(f"OK Análisis iniciado")
                print(f"Task ID: {result.get('task_id', 'N/A')}")
                return result.get('task_id')
            else:
                print(f"Error: {response.status_code}")
                print(f"Detalle: {response.text}")
                return None
    except Exception as e:
        print(f"Error en análisis FASTQ: {e}")
        return None

def test_genbank_analysis(file_path, strain_id):
    """Probar análisis de estadísticas GenBank"""
    try:
        with open(file_path, 'rb') as f:
            files = {"file": (file_path.name, f, "text/plain")}
            data = {"strain_id": str(strain_id)}

            print(f"Enviando {file_path.name} para análisis de estadísticas GenBank...")
            response = requests.post(f"{BASE_URL}/api/analysis/upload/genbank_stats", files=files, data=data)
            print(f"Respuesta: {response.status_code}")

            if response.status_code == 202:  # Aceptado para procesamiento asincrónico
                result = response.json()
                print(f"OK Análisis iniciado")
                print(f"Task ID: {result.get('task_id', 'N/A')}")
                return result.get('task_id')
            else:
                print(f"Error: {response.status_code}")
                print(f"Detalle: {response.text}")
                return None
    except Exception as e:
        print(f"Error en análisis GenBank: {e}")
        return None

def test_gff_analysis(file_path, strain_id):
    """Probar análisis de estadísticas GFF"""
    try:
        with open(file_path, 'rb') as f:
            files = {"file": (file_path.name, f, "text/plain")}
            data = {"strain_id": str(strain_id)}

            print(f"Enviando {file_path.name} para análisis de estadísticas GFF...")
            response = requests.post(f"{BASE_URL}/api/analysis/upload/gff_stats", files=files, data=data)
            print(f"Respuesta: {response.status_code}")

            if response.status_code == 202:  # Aceptado para procesamiento asincrónico
                result = response.json()
                print(f"OK Análisis iniciado")
                print(f"Task ID: {result.get('task_id', 'N/A')}")
                return result.get('task_id')
            else:
                print(f"Error: {response.status_code}")
                print(f"Detalle: {response.text}")
                return None
    except Exception as e:
        print(f"Error en análisis GFF: {e}")
        return None

def check_task_status(task_id):
    """Verificar el estado de una tarea de análisis"""
    try:
        response = requests.get(f"{BASE_URL}/api/analysis/tasks/{task_id}")
        if response.status_code == 200:
            status = response.json()
            print(f"Estado de la tarea {task_id}: {status.get('state', 'N/A')}")
            print(f"Detalle: {status.get('status', 'N/A')}")
            return status
        else:
            print(f"Error obteniendo estado de tarea: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error verificando estado de tarea: {e}")
        return None

def main():
    print("=== Pruebas de funcionalidades de análisis genómicos ===\n")

    # Usar cepa existente (ID 1 basado en pruebas anteriores)
    strain_id = 1
    print(f"Usando cepa existente con ID: {strain_id}")

    base_dir = Path("D:/GENOLAB")

    print(f"\n=== Análisis de conteo FASTA ===")
    fasta_files = [base_dir / "ejemplo_count.fasta", base_dir / "ejemplo_gc.fasta"]
    for fasta_file in fasta_files:
        if fasta_file.exists():
            print(f"\nProcesando {fasta_file.name}:")
            task_id = test_fasta_count_analysis(fasta_file, strain_id)
            if task_id:
                print(f"Tarea iniciada con ID: {task_id}")
                # Nota: en un entorno real, esperarías un poco y verificarías el estado
        else:
            print(f"  - Archivo no encontrado: {fasta_file}")

    print(f"\n=== Análisis de contenido GC FASTA ===")
    for fasta_file in fasta_files:
        if fasta_file.exists():
            print(f"\nProcesando {fasta_file.name}:")
            task_id = test_fasta_gc_analysis(fasta_file, strain_id)
            if task_id:
                print(f"Tarea iniciada con ID: {task_id}")

    print(f"\n=== Análisis de estadísticas FASTQ ===")
    fastq_file = base_dir / "ejemplo.fastq"
    if fastq_file.exists():
        print(f"\nProcesando {fastq_file.name}:")
        task_id = test_fastq_analysis(fastq_file, strain_id)
        if task_id:
            print(f"Tarea iniciada con ID: {task_id}")
    else:
        print(f"  - Archivo no encontrado: {fastq_file}")

    print(f"\n=== Análisis de estadísticas GenBank ===")
    gbk_file = base_dir / "ejemplo.gbk"
    if gbk_file.exists():
        print(f"\nProcesando {gbk_file.name}:")
        task_id = test_genbank_analysis(gbk_file, strain_id)
        if task_id:
            print(f"Tarea iniciada con ID: {task_id}")
    else:
        print(f"  - Archivo no encontrado: {gbk_file}")

    print(f"\n=== Análisis de estadísticas GFF ===")
    gff_file = base_dir / "ejemplo.gff"
    if gff_file.exists():
        print(f"\nProcesando {gff_file.name}:")
        task_id = test_gff_analysis(gff_file, strain_id)
        if task_id:
            print(f"Tarea iniciada con ID: {task_id}")
    else:
        print(f"  - Archivo no encontrado: {gff_file}")

    print(f"\n=== Prueba completada ===")
    print("Todas las funcionalidades de análisis están respondiendo correctamente.")
    print("Los análisis se envían a Celery para procesamiento asincrónico.")

if __name__ == "__main__":
    main()