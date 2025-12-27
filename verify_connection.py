#!/usr/bin/env python3
"""
Script para verificar la conexión entre frontend y backend
"""
import requests
import sys

def check_backend_connection():
    """Verifica si el backend está accesible"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("[OK] Backend accesible en http://localhost:8000")
            print(f"  Estado: {response.json().get('status', 'desconocido')}")
            return True
        else:
            print(f"[ERROR] Backend no accesible. Código de estado: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se puede conectar al backend en http://localhost:8000")
        return False
    except Exception as e:
        print(f"[ERROR] Error al conectar con el backend: {e}")
        return False

def check_organisms_endpoint():
    """Verifica si el endpoint de organismos está funcionando"""
    try:
        response = requests.get("http://localhost:8000/api/ceparium/organisms/", timeout=5)
        if response.status_code == 200:
            organisms = response.json()
            print(f"[OK] Endpoint de organismos accesible. Número de organismos: {len(organisms)}")
            return True
        else:
            print(f"[ERROR] Endpoint de organismos no accesible. Código de estado: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Error al acceder al endpoint de organismos: {e}")
        return False

def main():
    print("Verificando conexión entre frontend y backend...")
    print("="*50)

    backend_ok = check_backend_connection()
    if backend_ok:
        organisms_ok = check_organisms_endpoint()

    print("="*50)
    if backend_ok:
        print("[OK] Backend está corriendo y accesible")
        if 'organisms_ok' in locals() and organisms_ok:
            print("[OK] API de organismos está funcionando correctamente")
            print("\nEl problema podría estar en el frontend o en la configuración de CORS.")
        else:
            print("[ERROR] El endpoint de organismos no está respondiendo")
    else:
        print("[ERROR] Backend no está accesible. Verifica que esté corriendo en el puerto 8000.")

if __name__ == "__main__":
    main()