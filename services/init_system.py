"""
Sistema de inicialización y restauración completa para Genolab
"""
import os
import sys
import sqlite3
from pathlib import Path

# Agregar la carpeta services al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from restore_data import restore_from_backup_json_files
from app.database import SessionLocal
from app import crud, schemas
from app.core.config import settings


def check_database_exists():
    """Verifica si la base de datos existe y tiene datos"""
    db_path = Path("services", "genolab.db")
    if not db_path.exists():
        print("Base de datos no encontrada")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si hay tablas y datos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall() if table[0] not in ['sqlite_sequence', 'sqlite_master']]
        
        if not tables:
            print("Base de datos encontrada pero sin tablas")
            conn.close()
            return False
        
        # Contar registros en cada tabla importante
        important_tables = ['users', 'organisms', 'strains', 'analyses']
        has_data = False
        
        for table in important_tables:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                if count > 0:
                    has_data = True
                    break
        
        conn.close()
        return has_data
        
    except sqlite3.Error:
        return False


def initialize_database():
    """Inicializa la base de datos si no existe o está vacía"""
    from create_db import create_db, create_default_user
    
    print("Inicializando base de datos...")
    create_db()
    create_default_user()
    print("Base de datos inicializada")


def restore_system():
    """Restaura el sistema completo desde backups"""
    print("Restaurando sistema desde backup...")
    
    # Verificar si existen archivos de backup
    backup_files = ['backup_users.json', 'backup_organisms.json', 'backup_strains.json', 'backup_analyses.json']
    backup_dir = Path(".")  # Directorio actual
    
    existing_backups = [f for f in backup_files if (backup_dir / f).exists()]
    
    if not existing_backups:
        print("No se encontraron archivos de backup para restaurar")
        print("Creando base de datos con datos predeterminados...")
        initialize_database()
        return False
    
    print(f"Archivos de backup encontrados: {existing_backups}")
    
    success = restore_from_backup_json_files(str(backup_dir))
    if success:
        print("Sistema restaurado exitosamente desde backup")
        return True
    else:
        print("Falló la restauración desde backup")
        print("Creando base de datos con datos predeterminados...")
        initialize_database()
        return False


def main():
    print("Sistema de Inicialización - Genolab")
    print("="*40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "force":
        print("Forzando restauración desde backup...")
        restore_system()
        return
    
    print("Verificando estado del sistema...")
    
    # Verificar si la base de datos existe y tiene datos
    db_has_data = check_database_exists()
    
    if db_has_data:
        print("Sistema ya inicializado con datos existentes")
        print("No es necesario restaurar desde backup")
    else:
        print("Base de datos no encontrada o sin datos")
        restore_choice = input("¿Desea restaurar desde backup disponible? (s/n, por defecto n): ").lower()
        
        if restore_choice in ['s', 'y', 'si', 'yes']:
            restore_system()
        else:
            print("Creando base de datos con datos predeterminados...")
            initialize_database()
    
    print("\nSistema de Genolab listo para usar")


if __name__ == "__main__":
    main()