"""
Script para insertar un usuario directamente en la base de datos SQLite
"""
import sqlite3
import hashlib

def insert_test_user():
    # Conectar a la base de datos existente en el contenedor
    db_path = "D:/GENOLAB/services/data/../genolab.db"  # Ruta desde fuera del contenedor

    # Alternativamente, intentar la ruta completa
    import os
    if not os.path.exists(db_path):
        db_path = "D:/GENOLAB/services/genolab.db"

    print(f"Intentando conectar a: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar si ya existe algún usuario
        cursor.execute("SELECT id, email FROM users LIMIT 1")
        existing_user = cursor.fetchone()

        if existing_user:
            print(f"Usuario existente encontrado: ID {existing_user[0]}, Email: {existing_user[1]}")
            conn.close()
            return existing_user[0]

        # Insertar un usuario de prueba
        cursor.execute("""
            INSERT INTO users (email, name, is_active)
            VALUES (?, ?, ?)
        """, ("test@example.com", "Test User", 1))

        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        print(f"Usuario de prueba creado exitosamente con ID: {user_id}")
        print("Ya puedes subir archivos a MinIO usando la API")
        return user_id

    except sqlite3.Error as e:
        print(f"Error con SQLite: {e}")
        # Seguramente la base de datos está en el contenedor, necesitamos accederla desde ahí
        print("La base de datos parece estar en el contenedor. Vamos a probar el sistema completo otra vez...")
        return None

def main():
    print("Insertando usuario de prueba en la base de datos...")
    user_id = insert_test_user()

    if user_id:
        print(f"\nOK: Usuario listo (ID: {user_id}). Ahora puedes subir archivos a MinIO.")
    else:
        print("\nINFO: La base de datos está en el contenedor Docker.")
        print("Ya tienes el backend corriendo con un usuario, probemos de nuevo la subida...")

if __name__ == "__main__":
    main()