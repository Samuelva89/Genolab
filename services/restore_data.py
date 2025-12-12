"""
Script de restauración mejorado para Genolab
Compatible con los archivos de backup existentes (backup_*.json)
"""
import sqlite3
import json
import os
from datetime import datetime
import sys
from pathlib import Path


def restore_from_backup_json_files(backup_dir: str = "."):
    """Restaura datos de los archivos JSON de backup existentes"""
    print("Restaurando datos desde archivos JSON de backup...")

    # Ruta de la base de datos - usar la ubicación configurada en settings
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from app.core.config import settings

    # Extraer la ruta de la base de datos del URL de SQLAlchemy
    if settings.SQLALCHEMY_DATABASE_URL.startswith("sqlite:///"):
        db_path = settings.SQLALCHEMY_DATABASE_URL[10:]  # Remover "sqlite:///"
    else:
        # Si no es SQLite, usar path predeterminado
        db_path = os.path.join("services", "genolab.db")

    # Archivos de backup existentes
    backup_files = {
        'users': 'backup_users.json',
        'organisms': 'backup_organisms.json',
        'strains': 'backup_strains.json',
        'analyses': 'backup_analyses.json'
    }

    # Verificar que existan los archivos de backup
    missing_files = []
    for table, filename in backup_files.items():
        filepath = os.path.join(backup_dir, filename)
        if not os.path.exists(filepath):
            missing_files.append(filename)

    if missing_files:
        print(f"Archivos de backup faltantes: {missing_files}")
        print("Por favor, asegúrese de que todos los archivos de backup estén presentes.")
        return False

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Limpiar tablas existentes (en orden inverso para respetar claves foráneas)
        print("Limpiando tablas existentes...")
        tables_to_clear = ['analyses', 'strains', 'organisms', 'users']

        for table in reversed(tables_to_clear):
            cursor.execute(f"DELETE FROM {table}")

        # Restaurar usuarios
        print("Restaurando usuarios...")
        with open(os.path.join(backup_dir, backup_files['users']), 'r', encoding='utf-8') as f:
            users_data = json.load(f)

        for user in users_data:
            cursor.execute(
                "INSERT INTO users (id, email, name, is_active) VALUES (?, ?, ?, ?)",
                (user['id'], user['email'], user['name'], user['is_active'])
            )

        # Restaurar organismos
        print("Restaurando organismos...")
        with open(os.path.join(backup_dir, backup_files['organisms']), 'r', encoding='utf-8') as f:
            organisms_data = json.load(f)

        for organism in organisms_data:
            cursor.execute(
                "INSERT INTO organisms (id, name, genus, species) VALUES (?, ?, ?, ?)",
                (organism['id'], organism['name'], organism['genus'], organism['species'])
            )

        # Restaurar cepas
        print("Restaurando cepas...")
        with open(os.path.join(backup_dir, backup_files['strains']), 'r', encoding='utf-8') as f:
            strains_data = json.load(f)

        for strain in strains_data:
            cursor.execute(
                "INSERT INTO strains (id, strain_name, source, organism_id) VALUES (?, ?, ?, ?)",
                (strain['id'], strain['strain_name'], strain['source'], strain['organism_id'])
            )

        # Restaurar análisis
        print("Restaurando análisis...")
        with open(os.path.join(backup_dir, backup_files['analyses']), 'r', encoding='utf-8') as f:
            analyses_data = json.load(f)

        for analysis in analyses_data:
            # Convertir el campo results de dict a JSON string si es necesario
            results_json = analysis['results']
            if isinstance(results_json, dict):
                results_json = json.dumps(results_json)

            cursor.execute(
                "INSERT INTO analyses (id, analysis_type, results, file_url, timestamp, strain_id, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    analysis['id'],
                    analysis['analysis_type'],
                    results_json,
                    analysis['file_url'],
                    analysis['timestamp'],
                    analysis['strain_id'],
                    analysis['owner_id']
                )
            )

        # Confirmar cambios
        conn.commit()
        print(f"Restauración completada exitosamente!")
        print(f" - {len(users_data)} usuarios restaurados")
        print(f" - {len(organisms_data)} organismos restaurados")
        print(f" - {len(strains_data)} cepas restauradas")
        print(f" - {len(analyses_data)} análisis restaurados")

        # Mostrar resumen
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM organisms")
        organism_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM strains")
        strain_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM analyses")
        analysis_count = cursor.fetchone()[0]

        print(f"\nEstado actual de la base de datos:")
        print(f" - Usuarios: {user_count}")
        print(f" - Organismos: {organism_count}")
        print(f" - Cepas: {strain_count}")
        print(f" - Análisis: {analysis_count}")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"Error al restaurar la base de datos SQLite: {e}")
        if 'conn' in locals():
            conn.close()
        return False
    except json.JSONDecodeError as e:
        print(f"Error al leer los archivos JSON: {e}")
        return False
    except Exception as e:
        print(f"Error general: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.close()
        return False


def create_backup_json_files():
    """Crea archivos de backup JSON como los existentes"""
    db_path = os.path.join("services", "genolab.db")

    if not os.path.exists(db_path):
        print(f"No se encontró archivo de base de datos en: {db_path}")
        return

    print(f"Exportando datos de la base de datos: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Exportar cada tabla a un archivo JSON como en el sistema existente
        tables = ['users', 'organisms', 'strains', 'analyses']

        for table_name in tables:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            # Obtener los nombres de las columnas
            column_names = [description[0] for description in cursor.description]

            # Convertir filas a diccionarios
            data = []
            for row in rows:
                record = {}
                for i, col_name in enumerate(column_names):
                    value = row[i]
                    # Si es un campo JSON, intentar parsearlo
                    if col_name in ['results'] and value:
                        try:
                            record[col_name] = json.loads(value)
                        except:
                            record[col_name] = value
                    else:
                        record[col_name] = value
                data.append(record)

            # Guardar en archivo JSON
            filename = f"backup_{table_name}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

            print(f"  Exportados {len(data)} registros de '{table_name}' a '{filename}'")

        conn.close()
        print(f"\nDatos exportados exitosamente a archivos JSON")

    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos SQLite: {e}")
    except Exception as e:
        print(f"Error general: {e}")


def show_database_summary():
    """Muestra un resumen de la base de datos actual"""
    db_path = os.path.join("services", "genolab.db")

    if not os.path.exists(db_path):
        print(f"No se encontró archivo de base de datos en: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("Resumen de la base de datos actual:")
        print("="*40)

        # Contar registros en cada tabla
        tables = ['users', 'organisms', 'strains', 'analyses']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table.capitalize()}: {count} registros")

        # Mostrar algunos datos de ejemplo
        print("\nDatos de ejemplo:")

        # Usuarios
        cursor.execute("SELECT id, email, name FROM users LIMIT 3")
        users = cursor.fetchall()
        print(f"\nUsuarios (máximo 3):")
        for user in users:
            print(f"  ID: {user[0]}, Email: {user[1]}, Nombre: {user[2]}")

        # Organismos
        cursor.execute("SELECT id, name, genus, species FROM organisms LIMIT 3")
        organisms = cursor.fetchall()
        print(f"\nOrganismos (máximo 3):")
        for org in organisms:
            print(f"  ID: {org[0]}, Nombre: {org[1]}, Género: {org[2]}, Especie: {org[3]}")

        # Análisis recientes
        cursor.execute("SELECT id, analysis_type, timestamp FROM analyses ORDER BY timestamp DESC LIMIT 3")
        analyses = cursor.fetchall()
        print(f"\nAnálisis recientes (máximo 3):")
        for analysis in analyses:
            print(f"  ID: {analysis[0]}, Tipo: {analysis[1]}, Fecha: {analysis[2]}")

        conn.close()

    except sqlite3.Error as e:
        print(f"Error al leer la base de datos: {e}")
    except Exception as e:
        print(f"Error general: {e}")


def main():
    print("Sistema de Backup y Restauración - Genolab")
    print("="*50)

    if len(sys.argv) < 2:
        print("\nOpciones disponibles:")
        print("  python restore_data.py restore      - Restaurar desde archivos JSON")
        print("  python restore_data.py backup       - Crear archivos JSON de backup")
        print("  python restore_data.py status       - Mostrar estado actual")
        print("  python restore_data.py help         - Mostrar esta ayuda")
        return

    command = sys.argv[1]

    if command == "restore":
        print("Restaurando datos desde archivos JSON de backup...")
        success = restore_from_backup_json_files()
        if success:
            print("\n¡Restauración completada exitosamente!")
            print("Los datos han sido restaurados en la base de datos.")
        else:
            print("\nLa restauración falló. Por favor revise los mensajes de error.")

    elif command == "backup":
        print("Creando archivos JSON de backup...")
        create_backup_json_files()

    elif command == "status":
        print("Estado actual de la base de datos:")
        show_database_summary()

    elif command == "help":
        print("\nSistema de Backup y Restauración para Genolab")
        print("Este sistema permite:")
        print("- Restaurar datos desde archivos JSON de backup (backup_*.json)")
        print("- Crear nuevos archivos de backup JSON")
        print("- Verificar el estado actual de la base de datos")
        print("\nLos archivos de backup existentes son compatibles:")
        print("- backup_users.json")
        print("- backup_organisms.json")
        print("- backup_strains.json")
        print("- backup_analyses.json")

    else:
        print(f"Comando desconocido: {command}")
        print("Use 'python restore_data.py help' para ver la ayuda")


if __name__ == "__main__":
    main()