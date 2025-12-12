"""
Sistema de backup automático para Genolab
Crea backups regulares y gestiona el ciclo de vida de los backups
"""
import schedule
import time
import datetime
import os
import sys
from pathlib import Path

# Agregar la carpeta services al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backup_professional import BackupSystem


def create_automated_backup():
    """Crea un backup automático con nombre descriptivo"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"auto_backup_{timestamp}"
    
    try:
        backup_system = BackupSystem()
        backup_path = backup_system.create_backup(backup_name)
        print(f"[{datetime.datetime.now()}] Backup automático completado: {backup_path}")
        return True
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error en backup automático: {e}")
        return False


def cleanup_old_backups():
    """Limpia backups antiguos manteniendo solo los últimos 5"""
    try:
        backup_system = BackupSystem()
        backup_system.cleanup_old_backups(keep_last_n=5)
        print(f"[{datetime.datetime.now()}] Limpieza de backups antiguos completada")
        return True
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error en limpieza de backups: {e}")
        return False


def main():
    print("Sistema de Backup Automático - Genolab")
    print("="*50)
    
    if len(sys.argv) > 1:
        # Modo manual - crear un backup inmediato
        if sys.argv[1] == "now":
            print("Creando backup automático ahora...")
            success = create_automated_backup()
            if success:
                print("Backup automático creado exitosamente")
            else:
                print("Error al crear backup automático")
            return
        elif sys.argv[1] == "cleanup":
            print("Limpiando backups antiguos...")
            success = cleanup_old_backups()
            if success:
                print("Limpieza de backups completada")
            else:
                print("Error en la limpieza de backups")
            return
        else:
            print("Parámetros inválidos")
            print("Uso: python auto_backup.py [now|cleanup]")
            return
    
    # Modo automático - ejecutar según programación
    print("Iniciando sistema de backup automático...")
    print("Programación actual:")
    print("  - Backup completo cada 6 horas")
    print("  - Limpieza de backups cada día a las 2 AM")
    print("\nPresione Ctrl+C para detener el sistema")
    
    # Programar tareas
    schedule.every(6).hours.do(create_automated_backup)  # Cada 6 horas
    schedule.every().day.at("02:00").do(cleanup_old_backups)  # A las 2 AM
    
    # Crear un backup inicial
    print("\nCreando backup inicial...")
    create_automated_backup()
    
    # Bucle principal
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
    except KeyboardInterrupt:
        print("\n\nSistema de backup detenido por el usuario")
        print("Los datos están seguros con el último backup creado.")


if __name__ == "__main__":
    main()