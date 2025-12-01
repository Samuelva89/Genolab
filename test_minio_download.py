"""
Prueba de descarga de archivos desde MinIO
"""
import requests
import json
from pathlib import Path

# Configura la URL base del backend
BASE_URL = "http://localhost:8000"

def test_file_download(analysis_id):
    """Descargar un archivo específico por ID de análisis"""
    try:
        print(f"Intentando descargar archivo del análisis con ID {analysis_id}...")
        response = requests.get(f"{BASE_URL}/api/analysis/{analysis_id}/download")
        print(f"Respuesta de descarga: {response.status_code}")

        if response.status_code == 200:
            # Guardar el archivo descargado
            content_disposition = response.headers.get('Content-Disposition', '')
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')
            else:
                filename = f"downloaded_file_{analysis_id}"
            
            with open(f"downloaded_{filename}", 'wb') as f:
                f.write(response.content)
            
            print(f"OK Archivo descargado exitosamente: {filename}")
            print(f"Tamaño del archivo: {len(response.content)} bytes")
            return True
        elif response.status_code == 404:
            print(f"Error: Análisis no encontrado o archivo no disponible")
            print(f"Detalle: {response.text}")
            return False
        else:
            print(f"Error en la descarga: {response.status_code}")
            print(f"Detalle del error: {response.text}")
            return False
    except Exception as e:
        print(f"Error descargando archivo: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_analysis_list():
    """Obtener lista de análisis para encontrar un ID para probar"""
    try:
        print("Obteniendo lista de análisis...")
        response = requests.get(f"{BASE_URL}/api/analysis/strain/1")
        print(f"Respuesta: {response.status_code}")

        if response.status_code == 200:
            analyses = response.json()
            print(f"Se encontraron {len(analyses)} análisis")
            if analyses:
                for analysis in analyses:
                    print(f"  - ID: {analysis['id']}, Tipo: {analysis['analysis_type']}, Fecha: {analysis['timestamp']}")
            return analyses
        else:
            print(f"Error al obtener análisis: {response.status_code}")
            print(f"Detalle: {response.text}")
            return []
    except Exception as e:
        print(f"Error obteniendo lista de análisis: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print("=== Prueba de descarga de archivos desde MinIO ===\n")

    # Primero obtener la lista de análisis para encontrar un ID válido
    analyses = get_analysis_list()
    
    if analyses:
        # Probar con el primer análisis disponible
        analysis_id = analyses[0]['id']
        print(f"\nUsando análisis ID: {analysis_id} para prueba de descarga")
        success = test_file_download(analysis_id)
        if success:
            print(f"OK Descarga exitosa del archivo")
        else:
            print(f"XXX Error en la descarga")
    else:
        print("No se encontraron análisis para probar la descarga")
        print("Por favor, suba un archivo primero usando test_final_minio.py")

    print(f"\n=== Prueba de descarga completada ===")

if __name__ == "__main__":
    main()