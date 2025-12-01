"""
Script para verificar los datos en la base de datos
"""
import sqlite3
import os

def check_database_sqlite():
    """Verificar la estructura y contenido de la base de datos SQLite directamente"""
    # Verificar en el directorio de servicios
    db_path = os.path.join("services", "genolab.db")

    if not os.path.exists(db_path):
        print(f"No se encontró archivo de base de datos en: {db_path}")
        return

    print(f"Conectando a la base de datos: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar estructura de la tabla 'analyses'
        print("\nColumnas en la tabla 'analyses':")
        cursor.execute("PRAGMA table_info(analyses)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]}) - Not Null: {col[3]}, Default: {col[4]}")

        # Verificar algunos registros de análisis
        print("\nPrimeros 10 registros de análisis:")
        cursor.execute("SELECT id, analysis_type, file_url, results, timestamp FROM analyses LIMIT 10")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  ID: {row[0]}, Tipo: {row[1]}, File URL: {row[2]}")
            print(f"  Resultados (truncado): {str(row[3])[:100]}...")
            print(f"  Fecha: {row[4]}")
            print("  ---")

        # Contar total de análisis
        cursor.execute("SELECT COUNT(*) FROM analyses")
        total_count = cursor.fetchone()[0]
        print(f"\nTotal de análisis en la base de datos: {total_count}")

        # Verificar si hay análisis con file_url vacío o nulo
        cursor.execute("SELECT COUNT(*) FROM analyses WHERE file_url IS NULL OR file_url = ''")
        no_url_count = cursor.fetchone()[0]
        print(f"Análisis sin file_url: {no_url_count}")

        conn.close()
        print(f"\nConexión a la base de datos cerrada correctamente")

    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos SQLite: {e}")
    except Exception as e:
        print(f"Error general: {e}")

if __name__ == "__main__":
    check_database_sqlite()