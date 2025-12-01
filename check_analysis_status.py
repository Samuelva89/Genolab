"""
Verificación del estado de tareas de análisis
"""
import requests
import json

# Configura la URL base del backend
BASE_URL = "http://localhost:8000"

def check_task_status(task_id):
    """Verificar el estado de una tarea de análisis"""
    try:
        response = requests.get(f"{BASE_URL}/api/analysis/tasks/{task_id}")
        if response.status_code == 200:
            status = response.json()
            print(f"Estado de la tarea {task_id}: {status.get('state', 'N/A')}")
            print(f"Detalle: {status.get('status', 'N/A')}")
            if status.get('state') == 'SUCCESS':
                print(f"Resultados: {json.dumps(status.get('result', {}), indent=2)}")
            return status
        else:
            print(f"Error obteniendo estado de tarea: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error verificando estado de tarea: {e}")
        return None

def main():
    print("=== Verificación del estado de tareas de análisis ===\n")
    
    # IDs de tareas de las pruebas anteriores
    task_ids = [
        "12ec6476-2c73-4ca7-98eb-9de259cd02db",  # conteo FASTA ejemplo_count.fasta
        "779cc4c7-c47f-448d-a86d-a9344712f362",  # conteo FASTA ejemplo_gc.fasta
        "4d081d36-c4a8-4b47-b3af-0f46a5808960",  # contenido GC ejemplo_count.fasta
        "e4704eda-91cb-4c89-807a-412272a17800",  # contenido GC ejemplo_gc.fasta
        "fa4ea4b0-d480-472e-86a1-f7df85493492",  # estadísticas FASTQ
        "ce32773d-9fd3-4f98-b585-c67385754b27",  # estadísticas GenBank
        "860afd54-bf00-4bdb-a709-36af7f9627c9"   # estadísticas GFF
    ]
    
    for i, task_id in enumerate(task_ids):
        print(f"Verificando tarea {i+1} ({task_id}):")
        check_task_status(task_id)
        print("-" * 50)

if __name__ == "__main__":
    main()