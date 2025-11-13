# Importamos lo necesario desde nuestro archivo de configuración de la base de datos.
from .database import SessionLocal

# --- Dependencia para la Sesión de Base de Datos ---
# Esta es una función "generadora" de Python.
# FastAPI la usará para crear una sesión de base de datos por cada petición.
def get_db():
    # Crea un objeto de sesión.
    db = SessionLocal()
    try:
        # 'yield' entrega la sesión de base de datos al endpoint que la solicitó.
        # El código del endpoint se ejecuta en este punto.
        yield db
    finally:
        # Después de que el endpoint termina (incluso si hay un error),
        # el bloque 'finally' se asegura de que la sesión se cierre.
        # Esto es CRUCIAL para liberar la conexión a la base de datos y evitar problemas.
        db.close()