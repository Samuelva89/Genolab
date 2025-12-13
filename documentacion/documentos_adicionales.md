# Documentación Adicional para Entrega del Software - Genolab

## Tabla de Contenidos

1. [Licencia del Software](#licencia-del-software)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Pruebas y Validación](#pruebas-y-validación)
5. [Mantenimiento y Soporte](#mantenimiento-y-soporte)
6. [Seguridad y Privacidad](#seguridad-y-privacidad)
7. [Política de Backup](#política-de-backup)
8. [Versionado del Software](#versionado-del-software)

## Licencia del Software

### Tipo de Licencia
Genolab se distribuye bajo la licencia MIT, que permite:
- Uso comercial y privado
- Modificación del código fuente
- Distribución
- Uso patentado

### Términos de la Licencia
El software se proporciona "tal cual", sin garantías de ningún tipo. Los desarrolladores no asumen responsabilidad por daños directos, indirectos, accidentales, especiales o consecuentes resultantes del uso del software.

## Requisitos del Sistema

### Requisitos Mínimos

#### Hardware
- Procesador: 2 cores, 2.0 GHz o superior
- RAM: 4 GB
- Almacenamiento: 10 GB disponibles
- Red: Conexión Ethernet o Wi-Fi

#### Software
- Sistema Operativo: Linux, Windows 10+, macOS 10.14+
- Docker: Versión 20.10 o superior
- Docker Compose: Versión 2.0 o superior
- Python: 3.11 o superior
- Node.js: 18 o superior (solo para desarrollo frontend)

### Requisitos Recomendados

#### Hardware
- Procesador: 4 cores, 2.5 GHz o superior
- RAM: 8 GB
- Almacenamiento: 50 GB disponibles
- Red: Conexión de alta velocidad

#### Software
- Sistema Operativo: Linux Ubuntu 20.04 LTS o superior
- Docker: Versión 24.0 o superior
- Docker Compose: Versión 2.15 o superior

## Instalación y Configuración

### Instalación desde Contenedores Docker

#### Prerrequisitos
1. Instalar Docker y Docker Compose
2. Verificar que ambos servicios estén corriendo

#### Pasos de Instalación
1. Clonar el repositorio:
   ```
   git clone https://github.com/usuario/genolab.git
   cd genolab
   ```

2. Configurar variables de entorno:
   ```
   cp services/.env.example services/.env
   ```
   Editar el archivo `.env` con las configuraciones adecuadas

3. Iniciar servicios con Docker Compose:
   ```
   docker-compose up -d
   ```

4. Acceder a la aplicación:
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000
   - Documentación API: http://localhost:8000/docs
   - Consola MinIO: http://localhost:9001 (credenciales: minioadmin/minioadmin123)

### Configuración Inicial

#### Variables de Entorno Obligatorias

##### Backend (services/.env)
- `SQLALCHEMY_DATABASE_URL`: URL de conexión a base de datos
- `MINIO_ENDPOINT`: URL del servidor MinIO
- `MINIO_ACCESS_KEY`: Clave de acceso a MinIO
- `MINIO_SECRET_KEY`: Clave secreta de MinIO
- `MINIO_BUCKET_NAME`: Nombre del bucket para archivos
- `REDIS_URL`: URL de conexión a Redis

##### Frontend (.env.production)
- `VITE_API_URL`: URL del backend API

### Configuración de Producción

#### Recomendaciones
1. Usar contraseñas fuertes para todos los servicios
2. Configurar SSL/TLS para conexiones
3. Implementar balanceo de carga para múltiples instancias
4. Configurar monitoreo y logging
5. Establecer políticas de backup automáticas

## Pruebas y Validación

### Tipos de Pruebas Implementadas

#### Pruebas Unitarias
- Validación de funciones de negocio
- Pruebas de modelos de datos
- Pruebas de esquemas Pydantic
- Pruebas de utilidades y validaciones

#### Pruebas de Integración
- Flujos completos de subida y análisis
- Validación de APIs
- Pruebas de integración con MinIO
- Pruebas de integración con base de datos

#### Pruebas de Sistema
- Pruebas E2E de la aplicación completa
- Validación de flujos de usuario
- Pruebas de carga y rendimiento
- Pruebas de seguridad

### Ejecución de Pruebas

#### Backend
```
cd services
python -m pytest tests/ -v
```

#### Frontend
```
cd frontend
npm test
```

### Matriz de Pruebas
- 100% de cobertura para funciones críticas
- Validación de tipos de archivo aceptados
- Pruebas de validación de formato bioinformático
- Pruebas de procesamiento asincrónico

## Mantenimiento y Soporte

### Procedimientos de Mantenimiento

#### Diario
- Verificación de logs del sistema
- Monitoreo de espacio en disco
- Validación de servicios activos
- Revisión de tareas Celery pendientes

#### Semanal
- Backup automatizado de datos
- Limpieza de archivos temporales
- Actualización de dependencias (si procede)
- Revisión de seguridad de sistemas

#### Mensual
- Análisis de rendimiento del sistema
- Revisión de uso y estadísticas
- Actualización de software (si disponible)
- Documentación de cambios e incidencias

### Procedimientos de Soporte

#### Niveles de Soporte
- **Nivel 1**: Soporte funcional para usuarios
- **Nivel 2**: Soporte técnico para problemas de configuración
- **Nivel 3**: Soporte especializado para problemas de desarrollo

#### Canales de Soporte
- Documentación en línea
- Sistema de tickets
- Correo electrónico de soporte
- Formulario de contacto en la aplicación

## Seguridad y Privacidad

### Medidas de Seguridad Implementadas

#### API Security
- Rate limiting para prevenir ataque de fuerza bruta
- Validación de entradas (Pydantic schemas)
- Sanitización de datos
- Autenticación JWT (en desarrollo)

#### Almacenamiento de Datos
- Cifrado de archivos en MinIO
- ACLs configuradas para control de acceso
- Almacenamiento seguro de credenciales
- Registro de acceso a archivos

#### Validación de Archivos
- Validación de extensiones permitidas
- Verificación de tamaño máximo
- Escaneo de formato bioinformático
- Validación estructural de archivos

### Políticas de Privacidad

#### Datos del Usuario
- Solo se almacena información necesaria para la funcionalidad
- No se comparten datos con terceros
- Los usuarios pueden solicitar eliminación de sus datos
- Los datos se almacenan en servidores seguros

#### Archivos Bioinformáticos
- Los archivos se mantienen confidenciales
- Solo el propietario tiene acceso a sus archivos
- No se realizan análisis estadísticos que comprometan la privacidad
- Los archivos se pueden eliminar por el usuario

## Política de Backup

### Frecuencia de Backups

#### Diario
- Backup completo de base de datos
- Copia de metadatos de análisis
- Copia de configuración del sistema
- Registro de versiones de software

#### Semanal
- Backup incremental de archivos en MinIO
- Copia de scripts de recuperación
- Validación de integridad de backups

#### Mensual
- Backup completo de todo el sistema
- Prueba de restauración completa
- Evaluación de estrategia de backup

### Procedimientos de Recuperación

#### Recuperación de Base de Datos
1. Detener servicios activos
2. Restaurar base de datos desde backup
3. Verificar integridad de datos
4. Reiniciar servicios

#### Recuperación de Archivos
1. Recuperar archivos desde backup de MinIO
2. Verificar integridad de archivos
3. Actualizar referencias en base de datos
4. Validar accesibilidad

## Versionado del Software

### Estrategia de Versionado

Genolab sigue el patrón de versionado semántico (SemVer):
- **MAJOR**: Cambios incompatibles con versiones anteriores
- **MINOR**: Nuevas funcionalidades compatibles
- **PATCH**: Correcciones de errores

### Versiones Actuales
- API Backend: v0.3.0
- Frontend: v1.0.0
- Documentación: v1.0.0

### Política de Actualización
- Las versiones MINOR y PATCH son retrocompatibles
- Notificación de actualizaciones disponibles
- Procedimientos de migración documentados
- Prueba de actualizaciones en entorno de staging