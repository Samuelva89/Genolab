"""
Script para recuperar todos los datos de la base de datos SQLite
"""
import sqlite3
import json
import os
from datetime import datetime

def get_all_data_from_database():
    """Recuperar todos los datos de la base de datos"""
    db_path = os.path.join("services", "genolab.db")

    if not os.path.exists(db_path):
        print(f"No se encontró archivo de base de datos en: {db_path}")
        return

    print(f"Conectando a la base de datos: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tablas encontradas: {[table[0] for table in tables]}")
        print("\n" + "="*60)

        # Recuperar datos de cada tabla
        for table in tables:
            table_name = table[0]
            if table_name in ['sqlite_sequence', 'sqlite_master']:  # Skip these system tables
                continue

            print(f"\n--- DATOS DE LA TABLA: {table_name} ---")

            # Obtener todos los registros de la tabla
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            # Obtener los nombres de las columnas
            column_names = [description[0] for description in cursor.description]
            print(f"Columnas: {column_names}")
            print(f"Total de registros: {len(rows)}")

            if rows:
                print("\nDatos:")
                for i, row in enumerate(rows):
                    print(f"  Registro {i+1}:")
                    for j, col_name in enumerate(column_names):
                        value = row[j]
                        # Si es un campo JSON, formatearlo legiblemente
                        if col_name == 'results' and value:
                            try:
                                json_value = json.loads(value)
                                print(f"    {col_name}: {json.dumps(json_value, indent=4, ensure_ascii=False)}")
                            except:
                                print(f"    {col_name}: {value}")
                        else:
                            print(f"    {col_name}: {value}")
                    print("  ---")
            else:
                print("  No hay datos en esta tabla")

        # Ahora hacer consultas más específicas para mostrar relaciones
        print("\n" + "="*60)
        print("--- DATOS ESPECÍFICOS ---")

        # Consultas específicas para usuarios
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        print(f"\nUsuarios encontrados: {len(users)}")
        for user in users:
            print(f"  ID: {user[0]}, Email: {user[1]}, Nombre: {user[2]}, Activo: {user[3]}")

        # Consultas específicas para organismos
        cursor.execute("SELECT * FROM organisms")
        organisms = cursor.fetchall()
        print(f"\nOrganismos encontrados: {len(organisms)}")
        for org in organisms:
            print(f"  ID: {org[0]}, Nombre: {org[1]}, Género: {org[2]}, Especie: {org[3]}")

        # Consultas específicas para cepas
        cursor.execute("SELECT * FROM strains")
        strains = cursor.fetchall()
        print(f"\nCepas encontradas: {len(strains)}")
        for strain in strains:
            print(f"  ID: {strain[0]}, Nombre: {strain[1]}, Fuente: {strain[2]}, Organismo ID: {strain[3]}")

        # Consultas específicas para análisis
        cursor.execute("SELECT * FROM analyses ORDER BY timestamp DESC")
        analyses = cursor.fetchall()
        print(f"\nAnálisis encontrados: {len(analyses)}")
        for analysis in analyses:
            print(f"  ID: {analysis[0]}, Tipo: {analysis[1]}")
            print(f"  Resultados: {str(analysis[2])[:100]}...")  # Truncar resultados
            print(f"  URL archivo: {analysis[3]}")
            print(f"  Fecha: {analysis[4]}")
            print(f"  Cepa ID: {analysis[5]}, Usuario ID: {analysis[6]}")
            print("  ---")

        conn.close()
        print(f"\nConexión a la base de datos cerrada correctamente")

    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos SQLite: {e}")
    except Exception as e:
        print(f"Error general: {e}")

def export_data_to_files():
    """Exportar datos a archivos JSON para su recuperación"""
    db_path = os.path.join("services", "genolab.db")

    if not os.path.exists(db_path):
        print(f"No se encontró archivo de base de datos en: {db_path}")
        return

    print(f"Exportando datos de la base de datos: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Exportar cada tabla a un archivo JSON
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

if __name__ == "__main__":
    print("=== RECUPERACIÓN DE DATOS DE LA BASE DE DATOS ===\n")

    print("1. Mostrando todos los datos en pantalla...")
    get_all_data_from_database()

    print("\n" + "="*60)
    print("2. Exportando datos a archivos JSON...")
    export_data_to_files()

    print("\n=== PROCESO COMPLETADO ===")