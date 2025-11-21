import os
from app.core.config import settings

print("Variables de entorno del sistema:")
print(f"MINIO_ENDPOINT: {os.getenv('MINIO_ENDPOINT')}")
print(f"MINIO_ACCESS_KEY: {os.getenv('MINIO_ACCESS_KEY')}")
print(f"MINIO_SECRET_KEY: {os.getenv('MINIO_SECRET_KEY')}")
print(f"MINIO_BUCKET_NAME: {os.getenv('MINIO_BUCKET_NAME')}")
print()

print("Valores desde settings:")
print(f"settings.MINIO_ENDPOINT: {settings.MINIO_ENDPOINT}")
print(f"settings.MINIO_ACCESS_KEY: {settings.MINIO_ACCESS_KEY}")
print(f"settings.MINIO_SECRET_KEY: {settings.MINIO_SECRET_KEY}")
print(f"settings.MINIO_BUCKET_NAME: {settings.MINIO_BUCKET_NAME}")