# Despliegue de Genolab en Render con MySQL

## Configuración del Proyecto

Este archivo explica cómo desplegar Genolab en Render usando MySQL como base de datos.

## Pasos para el Despliegue

1. **Preparar el Repositorio**
   - Asegúrate de que tu código esté en un repositorio GitHub
   - El archivo `render.yaml` en la raíz contiene la configuración del servicio

2. **Crear Servicio en Render**
   - Accede al dashboard de Render
   - Haz clic en "New +" y selecciona "Web Service"
   - Conecta tu repositorio GitHub
   - Usa la rama principal (`main`)

3. **Configuración del Servicio**
   - Directorio raíz: `services`
   - Entorno: `Python`
   - Comando de compilación: se encuentra en el archivo `render.yaml`
   - Comando de inicio: se encuentra en el archivo `render.yaml`
   - Ruta de verificación de salud: `/api/health`

4. **Variables de Entorno**
   - `MINIO_ENDPOINT`: URL de tu servicio MinIO/S3
   - `MINIO_ACCESS_KEY`: Clave de acceso
   - `MINIO_SECRET_KEY`: Clave secreta
   - `MINIO_BUCKET_NAME`: Nombre del bucket (por defecto: genolab-bucket)
   - `SECRET_KEY`: Clave secreta JWT (genera una con `openssl rand -hex 32`)

5. **Configuración de la Base de Datos**
   - El archivo `render.yaml` crea automáticamente:
     - Un servicio de base de datos MySQL
     - Un servicio Redis para Celery
     - La aplicación FastAPI

## Variables de Entorno Adicionales (Opcionales)

- `DEBUG`: `False` para producción
- `TESTING`: `False` para producción
- `MAX_UPLOAD_SIZE_MB`: Tamaño máximo de archivo (por defecto: 10)
- `ALLOWED_EXTENSIONS`: Extensiones permitidas (por defecto: fasta,fastq,gb,gff,fa,fq)

## Seguridad

- No almacenes credenciales en el código fuente
- Usa las funciones de variables de entorno encriptadas de Render
- Genera una clave secreta JWT fuerte para producción
- Activa autenticación de dos factores para tu cuenta de Render

## Solución de Problemas

### Problemas comunes

1. **Fallo en la conexión a la base de datos**
   - Verifica que el servicio MySQL esté activo
   - Confirma que las credenciales estén configuradas correctamente

2. **Fallo en carga de archivos**
   - Verifica las credenciales de MinIO/S3
   - Confirma que el bucket exista y tenga permisos adecuados

3. **Fallo en el inicio de la aplicación**
   - Revisa los logs en el dashboard de Render
   - Asegúrate de que todas las variables de entorno estén configuradas

## Escalabilidad

- Monitorea el uso de recursos en el dashboard de Render
- Ajusta el plan del servicio según sea necesario
- Considera usar CDN para activos estáticos si es necesario

## Actualizaciones

- Aplica actualizaciones de seguridad regularmente
- Prueba actualizaciones en entorno de staging primero
- Mantiene tu configuración bajo control de versiones