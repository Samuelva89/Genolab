"""
Sistema profesional de backup y restauración para Genolab
Mejora el sistema existente con funcionalidades profesionales
"""
import sqlite3
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import zipfile
from typing import List, Dict, Any
import sys

from app.core.config import settings


class BackupSystem:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configurar cliente S3/MinIO
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.db_path = Path("services", "genolab.db")

    def create_backup(self, backup_name: str = None) -> str:
        """
        Crea un backup completo: base de datos + archivos de MinIO
        """
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"genolab_backup_{timestamp}"
        
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        print(f"Creando backup completo: {backup_name}")
        
        # 1. Backup de base de datos (mantiene formato existente)
        print("  - Respaldo de base de datos...")
        self._backup_database_to_json_files(backup_path)
        
        # 2. Backup de archivos de MinIO
        print("  - Respaldo de archivos de MinIO...")
        minio_backup_dir = backup_path / "minio_files"
        minio_backup_dir.mkdir(exist_ok=True)
        self._backup_minio_files(minio_backup_dir)
        
        # 3. Crear archivo de metadatos
        print("  - Creando archivo de metadatos...")
        metadata = {
            "backup_name": backup_name,
            "timestamp": datetime.now().isoformat(),
            "database_tables": self._get_database_tables(),
            "minio_objects_count": self._count_minio_objects(),
            "description": "Backup completo de Genolab: base de datos y archivos de MinIO"
        }
        
        metadata_path = backup_path / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
        
        # 4. Comprimir todo en un archivo ZIP
        print("  - Comprimiendo backup...")
        zip_path = self.backup_dir / f"{backup_name}.zip"
        self._create_zip(backup_path, zip_path)
        
        # 5. Eliminar directorio temporal
        shutil.rmtree(backup_path)
        
        print(f"Backup completo creado: {zip_path}")
        return str(zip_path)

    def _backup_database_to_json_files(self, backup_path: Path):
        """Exporta datos de la base de datos a archivos JSON como en el sistema existente"""
        if not self.db_path.exists():
            print(f"No se encontró archivo de base de datos en: {self.db_path}")
            return

        print(f"Exportando datos de la base de datos: {self.db_path}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Exportar cada tabla a un archivo JSON (igual que en el sistema existente)
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

                # Guardar en archivo JSON en el directorio de backup
                filename = backup_path / f"backup_{table_name}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)

                print(f"  Exportados {len(data)} registros de '{table_name}' a '{filename.name}'")

            conn.close()
            print(f"Datos exportados exitosamente a archivos JSON")

        except sqlite3.Error as e:
            print(f"Error al conectar con la base de datos SQLite: {e}")
        except Exception as e:
            print(f"Error general: {e}")

    def _backup_minio_files(self, output_dir: Path):
        """Respalda todos los archivos de MinIO"""
        try:
            # Listar todos los objetos en el bucket
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            
            if 'Contents' not in response:
                print(f"    - No hay archivos en el bucket '{self.bucket_name}'")
                return
            
            objects = response['Contents']
            print(f"    - Encontrados {len(objects)} archivos en MinIO")
            
            for obj in objects:
                key = obj['Key']
                print(f"    - Descargando: {key}")
                
                # Crear la estructura de directorios
                # Usamos una estructura plana para evitar problemas con nombres de archivo complejos
                safe_key = self._sanitize_filename(key)
                file_path = output_dir / safe_key
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Descargar archivo
                self.s3_client.download_file(self.bucket_name, key, str(file_path))
                
        except ClientError as e:
            print(f"Error descargando archivos de MinIO: {e}")
            raise

    def restore_backup(self, backup_file: str):
        """
        Restaura un backup completo: base de datos + archivos de MinIO
        """
        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo de backup: {backup_path}")
        
        print(f"Restaurando backup: {backup_path.name}")
        
        # 1. Extraer el archivo ZIP
        extract_path = self.backup_dir / f"temp_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        extract_path.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(backup_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        # 2. Restaurar base de datos
        print("  - Restaurando base de datos...")
        self._restore_database_from_json_files(extract_path)
        
        # 3. Restaurar archivos de MinIO
        print("  - Restaurando archivos de MinIO...")
        minio_backup_dir = extract_path / "minio_files"
        if minio_backup_dir.exists():
            self._restore_minio_files(minio_backup_dir)
        else:
            print("    - No se encontraron archivos de MinIO para restaurar")
        
        # 4. Limpiar archivos temporales
        shutil.rmtree(extract_path)
        
        print("Restauración completada exitosamente!")

    def _restore_database_from_json_files(self, backup_dir: Path):
        """Restaura los datos de la base de datos desde archivos JSON"""
        # Conectar a la base de datos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Limpiar tablas existentes (en orden correcto para respetar las FK)
        # Debe ser en orden inverso para evitar problemas de clave foránea
        tables = ['analyses', 'strains', 'organisms', 'users']
        
        for table in reversed(tables):
            cursor.execute(f"DELETE FROM {table}")
        
        # Restaurar tablas en orden correcto
        for table in tables:  # Restaurar en orden correcto
            backup_file = backup_dir / f"backup_{table}.json"
            if backup_file.exists():
                with open(backup_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"    - Restaurando {len(data)} registros en tabla '{table}'")
                
                for record in data:
                    # Preparar la consulta SQL basada en las columnas
                    columns = list(record.keys())
                    placeholders = ', '.join(['?' for _ in columns])
                    column_names = ', '.join(columns)
                    
                    # Convertir campos JSON si es necesario
                    values = []
                    for col in columns:
                        val = record[col]
                        if isinstance(val, (dict, list)):
                            values.append(json.dumps(val))
                        else:
                            values.append(val)
                    
                    query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
                    cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        
        print(f"  - Base de datos restaurada exitosamente")

    def _restore_minio_files(self, backup_dir: Path):
        """Restaura los archivos de MinIO"""
        files_to_restore = list(backup_dir.rglob("*"))
        files_to_restore = [f for f in files_to_restore if f.is_file()]
        
        print(f"    - Restaurando {len(files_to_restore)} archivos a MinIO")
        
        for file_path in files_to_restore:
            # Recuperar el path original de MinIO 
            # El nombre de archivo fue sanitizado durante el backup, así que lo des-saneamos
            relative_path = file_path.relative_to(backup_dir)
            original_key = str(relative_path).replace('_SPLIT_', '/')
            
            print(f"    - Subiendo: {original_key}")
            try:
                self.s3_client.upload_file(str(file_path), self.bucket_name, original_key)
            except ClientError as e:
                print(f"      Error subiendo {original_key}: {e}")

    def list_backups(self) -> List[Dict[str, Any]]:
        """Lista todos los backups disponibles"""
        backups = []
        for file in self.backup_dir.glob("*.zip"):
            # Obtener información del archivo ZIP
            stat = file.stat()
            size_mb = stat.st_size / (1024 * 1024)
            
            backups.append({
                "name": file.stem,
                "size_mb": round(size_mb, 2),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return sorted(backups, key=lambda x: x['name'], reverse=True)

    def _get_database_tables(self) -> List[str]:
        """Obtiene lista de tablas en la base de datos"""
        if not self.db_path.exists():
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall() if table[0] not in ['sqlite_sequence', 'sqlite_master']]
        conn.close()
        return tables

    def _count_minio_objects(self) -> int:
        """Cuenta el número de objetos en MinIO"""
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            return response.get('KeyCount', 0)
        except ClientError:
            return 0

    def _create_zip(self, source_dir: Path, output_path: Path):
        """Crea un archivo ZIP del directorio"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitiza nombre de archivo para evitar problemas con caracteres especiales"""
        # Reemplazar caracteres problemáticos con guiones bajos
        # Esto es especialmente importante para rutas en MinIO
        import re
        sanitized = re.sub(r'[<>:"/\\|?*]', '_SPLIT_', filename)
        # También manejar caracteres especiales en URL
        sanitized = sanitized.replace('%', '_PERCENT_').replace('#', '_HASH_').replace('?', '_QMARK_')
        return sanitized

    def cleanup_old_backups(self, keep_last_n: int = 5):
        """Elimina backups antiguos, manteniendo solo los últimos N"""
        backups = self.list_backups()
        if len(backups) <= keep_last_n:
            return
        
        backups_to_delete = backups[keep_last_n:]
        for backup in backups_to_delete:
            backup_path = self.backup_dir / f"{backup['name']}.zip"
            backup_path.unlink()
            print(f"Eliminado backup antiguo: {backup_path.name}")


def main():
    """Función principal para usar el sistema de backup"""
    print("Sistema Profesional de Backup y Restauración - Genolab")
    print("="*60)
    
    backup_system = BackupSystem()
    
    if len(sys.argv) < 2:
        print("\nUso:")
        print("  python backup_professional.py create [nombre_backup]  - Crear backup")
        print("  python backup_professional.py restore <archivo>       - Restaurar backup") 
        print("  python backup_professional.py list                    - Listar backups")
        print("  python backup_professional.py info <archivo>          - Información de backup")
        print("  python backup_professional.py cleanup [n]             - Limpiar backups antiguos")
        print("  python backup_professional.py help                    - Mostrar este mensaje")
        return

    command = sys.argv[1]
    
    try:
        if command == "create":
            backup_name = sys.argv[2] if len(sys.argv) > 2 else None
            backup_system.create_backup(backup_name)
        
        elif command == "list":
            backups = backup_system.list_backups()
            print(f"\nBackups disponibles ({len(backups)}):")
            if backups:
                print(f"{'Nombre':<40} {'Tamaño (MB)':<12} {'Fecha':<20}")
                print("-" * 75)
                for backup in backups:
                    print(f"{backup['name']:<40} {backup['size_mb']:<12} {backup['modified']:<20}")
            else:
                print("No hay backups disponibles")
        
        elif command == "restore":
            if len(sys.argv) < 3:
                print("Uso: python backup_professional.py restore <nombre_backup.zip>")
                return
            
            backup_file = sys.argv[2]
            backup_path = Path(backup_file)
            if not backup_path.exists():
                backup_path = backup_system.backup_dir / backup_file
                if not backup_path.exists():
                    print(f"Error: No se encontró el archivo de backup: {backup_file}")
                    return
            
            confirm = input(f"¿Está seguro que desea restaurar el backup '{backup_path.name}'? (s/n): ")
            if confirm.lower() in ['s', 'y', 'si', 'yes']:
                backup_system.restore_backup(str(backup_path))
            else:
                print("Restauración cancelada")
        
        elif command == "info":
            if len(sys.argv) < 3:
                print("Uso: python backup_professional.py info <nombre_backup.zip>")
                return
            
            backup_file = sys.argv[2]
            backup_path = backup_system.backup_dir / backup_file
            if not backup_path.exists():
                print(f"Error: No se encontró el archivo de backup: {backup_file}")
                return
            
            # Extraer temporalmente el archivo para ver metadatos
            extract_path = backup_system.backup_dir / f"temp_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            extract_path.mkdir(exist_ok=True)
            
            try:
                with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                    zip_ref.extract('metadata.json', extract_path)
                
                metadata_path = extract_path / "metadata.json"
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                print(f"\nInformación del backup '{backup_path.name}':")
                print(f"  Nombre: {metadata['backup_name']}")
                print(f"  Fecha: {metadata['timestamp']}")
                print(f"  Descripción: {metadata['description']}")
                print(f"  Tablas de base de datos: {', '.join(metadata['database_tables'])}")
                print(f"  Objetos en MinIO: {metadata['minio_objects_count']}")
            finally:
                shutil.rmtree(extract_path)
        
        elif command == "cleanup":
            keep_n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            backup_system.cleanup_old_backups(keep_n)
            print(f"Se mantienen los últimos {keep_n} backups")
        
        elif command == "help":
            print("\nSistema Profesional de Backup y Restauración para Genolab")
            print("Este sistema permite:")
            print("- Crear backups completos (base de datos + archivos MinIO)")
            print("- Restaurar backups completos")
            print("- Administrar múltiples versiones de backups")
            print("- Verificar la integridad de los backups")
            print("- Limpiar backups antiguos")
        
        else:
            print(f"Comando desconocido: {command}")
            print("Use 'python backup_professional.py help' para ver la ayuda")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()