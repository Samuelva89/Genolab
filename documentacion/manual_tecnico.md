# Manual Técnico - Genolab

## Tabla de Contenidos

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Tecnologías Utilizadas](#tecnologías-utilizadas)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Componentes Principales](#componentes-principales)
5. [Flujo de Datos](#flujo-de-datos)
6. [Modelos de Datos](#modelos-de-datos)
7. [API Endpoints](#api-endpoints)
8. [Sistema de Análisis Asincrónico](#sistema-de-análisis-asincrónico)
9. [Configuración del Sistema](#configuración-del-sistema)
10. [Despliegue](#despliegue)
11. [Mantenimiento y Escalabilidad](#mantenimiento-y-escalabilidad)

## Arquitectura del Sistema

Genolab implementa una arquitectura de microservicios con patrón API REST, compuesta por:

- **Frontend**: Aplicación React con TypeScript para la interfaz de usuario
- **Backend**: API REST desarrollada con FastAPI en Python
- **Base de Datos**: PostgreSQL (en producción) o SQLite (en desarrollo)
- **Cola de Tareas**: Celery con Redis para procesamiento asincrónico
- **Almacenamiento de Objetos**: MinIO compatible con S3 para archivos bioinformáticos
- **Contenedores**: Docker y docker-compose para virtualización

### Patrón Arquitectónico

El sistema sigue el patrón MVC (Modelo-Vista-Controlador) con separación clara de responsabilidades:

- **Modelos**: Definidos con SQLAlchemy ORM
- **Vistas**: Componentes React en el frontend
- **Controladores**: Rutas FastAPI en el backend
- **Lógica de Negocio**: Funciones CRUD y servicios

## Tecnologías Utilizadas

### Backend
- **Python 3.11+**: Lenguaje principal
- **FastAPI**: Framework web moderno con soporte para asincronía
- **SQLAlchemy 2.0+**: ORM para manejo de base de datos
- **Pydantic 2.0+**: Validación de datos y serialización
- **Celery**: Procesamiento de tareas asincrónicas
- **Redis**: Broker de mensajes y caché
- **Boto3**: Cliente S3 para integración con MinIO
- **Biopython**: Biblioteca para análisis bioinformático
- **BCBio.GFF**: Biblioteca para procesamiento de archivos GFF

### Frontend
- **React 18+**: Biblioteca para interfaces de usuario
- **TypeScript**: Extensión tipada de JavaScript
- **Vite**: Herramienta de desarrollo y empaquetado
- **Axios**: Cliente HTTP para peticiones API
- **React Router DOM**: Enrutamiento de la aplicación
- **Zustand**: Gestión de estado global
- **Chart.js y React Chart.js 2**: Visualización de datos

### Infraestructura
- **Docker**: Contenedores para virtualización
- **Docker Compose**: Orquestación de servicios
- **MinIO**: Almacenamiento de objetos compatible S3
- **PostgreSQL**: Base de datos relacional (producción)
- **SQLite**: Base de datos relacional (desarrollo)

## Estructura del Proyecto

```
genolab/
├── frontend/                 # Aplicación React
│   ├── src/
│   │   ├── components/       # Componentes reutilizables
│   │   ├── pages/           # Páginas de la aplicación
│   │   ├── services/        # Servicios API y lógica de negocio
│   │   ├── Styles/          # Estilos CSS
│   │   └── assets/          # Recursos estáticos
│   ├── public/              # Recursos públicos
│   └── package.json         # Dependencias frontend
├── services/                # API Backend
│   ├── app/
│   │   ├── core/           # Configuración y utilidades
│   │   ├── models/         # Modelos de base de datos
│   │   ├── routers/        # Rutas API
│   │   ├── schemas/        # Esquemas Pydantic
│   │   ├── dependencies/   # Dependencias FastAPI
│   │   ├── tasks/          # Tareas Celery
│   │   ├── celery_worker/  # Configuración Celery
│   │   └── main.py         # Punto de entrada API
│   ├── requirements.txt     # Dependencias Python
│   └── Dockerfile           # Contenedor backend
├── docker-compose.yml       # Orquestación servicios
├── render.yaml              # Configuración despliegue Render
└── requirements.txt         # Dependencias proyecto
```

## Componentes Principales

### Backend

#### app/main.py
- Punto de entrada de la aplicación FastAPI
- Configuración de CORS, rate limiting y middleware
- Inclusión de rutas y manejo de ciclo de vida

#### app/models.py
- Definición de modelos ORM con SQLAlchemy
- Relaciones entre entidades: User, Organism, Strain, Analysis

#### app/schemas.py
- Esquemas Pydantic para validación de datos
- Definición de estructuras de entrada/salida API

#### app/routers/
- Modulos de rutas separados por funcionalidad
- users.py: Gestión de usuarios
- organisms.py: Gestión de organismos
- analysis.py: Análisis bioinformáticos
- stats.py: Estadísticas del sistema

#### app/tasks.py
- Tareas Celery para procesamiento asincrónico
- Análisis de archivos FASTA, FASTQ, GenBank, GFF

### Frontend

#### src/App.tsx
- Enrutamiento principal de la aplicación
- Integración con Sidebar y componentes principales

#### src/services/api.ts
- Configuración de cliente Axios
- Interceptors para manejo de errores y logging
- Configuración de URLs base según entorno

#### src/pages/
- Componentes de página para cada funcionalidad
- HomePage: Página principal con estadísticas
- OrganismListPage: Lista y gestión de organismos
- IndividualFileUploadPage: Subida de archivos

## Flujo de Datos

### Flujo de Subida y Análisis de Archivos

1. **Cliente**: Usuario selecciona archivo y tipo de análisis
2. **Frontend**: Envía archivo vía multipart form data a backend
3. **Backend**: Valida archivo y lo almacena en MinIO
4. **Backend**: Crea tarea Celery y devuelve ID de tarea
5. **Celery**: Procesa archivo desde MinIO según tipo de análisis
6. **Backend**: Guarda resultados en base de datos
7. **Cliente**: Consulta estado de tarea y resultados vía API
8. **Frontend**: Muestra resultados al usuario

### Flujo de Consulta de Datos

1. **Cliente**: Solicita datos a endpoints API
2. **Backend**: Valida permisos y autenticación
3. **Backend**: Consulta base de datos vía SQLAlchemy
4. **Backend**: Valida respuesta con esquemas Pydantic
5. **Cliente**: Recibe y procesa datos en formato JSON

## Modelos de Datos

### User
```python
id: int (primary key)
email: str (unique)
name: str (nullable)
is_active: bool (default True)
analyses: List[Analysis] (relationship)
```

### Organism
```python
id: int (primary key)
name: str
genus: str
species: str
strains: List[Strain] (relationship)
```

### Strain
```python
id: int (primary key)
strain_name: str
source: str
organism_id: int (foreign key)
organism: Organism (relationship)
analyses: List[Analysis] (relationship)
```

### Analysis
```python
id: int (primary key)
analysis_type: str
results: JSON (flexible dictionary)
file_url: str (URL MinIO)
timestamp: DateTime
strain_id: int (foreign key)
owner_id: int (foreign key)
strain: Strain (relationship)
owner: User (relationship)
```

## API Endpoints

### Autenticación y Usuarios
- `GET /api/users/` - Listar usuarios
- `POST /api/users/` - Crear usuario
- `GET /api/users/{id}` - Obtener usuario específico
- `PUT /api/users/{id}` - Actualizar usuario
- `DELETE /api/users/{id}` - Eliminar usuario

### Organismos
- `GET /api/organisms/` - Listar organismos
- `POST /api/organisms/` - Crear organismo
- `GET /api/organisms/{id}` - Obtener organismo específico
- `PUT /api/organisms/{id}` - Actualizar organismo
- `DELETE /api/organisms/{id}` - Eliminar organismo

### Cepas
- `GET /api/strains/` - Listar cepas
- `POST /api/strains/` - Crear cepa
- `GET /api/strains/{id}` - Obtener cepa específica

### Análisis
- `GET /api/analysis/strain/{strain_id}` - Análisis por cepa
- `POST /api/analysis/upload/raw` - Subida archivo sin análisis
- `POST /api/analysis/upload/fasta_count` - Análisis conteo FASTA
- `POST /api/analysis/upload/fasta_gc_content` - Análisis contenido GC
- `POST /api/analysis/upload/fastq_stats` - Análisis estadísticas FASTQ
- `POST /api/analysis/upload/genbank_stats` - Análisis GenBank
- `POST /api/analysis/upload/gff_stats` - Análisis GFF
- `GET /api/analysis/tasks/{task_id}` - Estado de tarea Celery
- `GET /api/analysis/{analysis_id}/results/download-txt` - Descargar resultados
- `GET /api/analysis/{analysis_id}/download` - Descargar archivo original

### Estadísticas
- `GET /api/stats/summary` - Estadísticas generales del sistema

## Sistema de Análisis Asincrónico

### Arquitectura de Tareas Asincrónicas

Genolab utiliza Celery para procesamiento asincrónico de archivos bioinformáticos, lo que permite:

- No bloquear la API durante análisis prolongados
- Procesar múltiples archivos simultáneamente
- Seguimiento del progreso de análisis
- Manejo robusto de errores

### Configuración Celery

- **Broker**: Redis (url: redis://localhost:6379/0)
- **Backend de Resultados**: Redis
- **Serializador**: JSON
- **Tiempo de espera**: Configurable
- **Reintentos**: Configurables para fallas transitorias

### Tipos de Tareas Disponibles

#### Análisis FASTA
- **process_fasta_count**: Cuenta secuencias en archivo FASTA
- **process_fasta_gc_content**: Calcula contenido GC promedio

#### Análisis FASTQ
- **process_fastq_stats**: Calcula estadísticas de calidad y longitud

#### Análisis GenBank
- **process_genbank_stats**: Extrae información de anotaciones

#### Análisis GFF
- **process_gff_stats**: Cuenta tipos de features en archivo GFF

### Manejo de Estado de Tareas

- **PENDING**: Tarea creada pero no iniciada
- **PROGRESS**: Tarea en ejecución (con porcentaje progreso)
- **SUCCESS**: Tarea completada exitosamente
- **FAILURE**: Tarea fallida con información de error

### Recuperación de Resultados

Los resultados se almacenan en base de datos como objetos JSON, permitiendo:
- Consultas flexibles sobre resultados
- Análisis posteriores
- Exportación en múltiples formatos

## Configuración del Sistema

### Variables de Entorno

#### Backend (.env)
- `SQLALCHEMY_DATABASE_URL`: URL conexión base de datos
- `MINIO_ENDPOINT`: URL servidor MinIO
- `MINIO_ACCESS_KEY`: Clave acceso MinIO
- `MINIO_SECRET_KEY`: Clave secreta MinIO
- `MINIO_BUCKET_NAME`: Nombre bucket MinIO
- `REDIS_URL`: URL conexión Redis
- `SECRET_KEY`: Clave secreta para tokens JWT
- `ALGORITHM`: Algoritmo para tokens JWT
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Tiempo expiración tokens

#### Frontend (.env)
- `VITE_API_URL`: URL backend API

### Configuración de Seguridad

- Rate limiting configurado (60 peticiones/minuto por IP)
- Validación de extensiones de archivo
- Tamaño máximo de subida configurable
- Almacenamiento seguro en MinIO
- Autenticación JWT (en desarrollo)

## Despliegue

### Docker Compose

El archivo docker-compose.yml define cinco servicios:

1. **minio**: Almacenamiento de objetos
2. **redis**: Broker de tareas Celery
3. **app**: Servicio backend FastAPI
4. **celery_worker**: Procesador de tareas asincrónicas
5. **frontend**: Aplicación React

### Despliegue en Render

El archivo render.yaml define:
- Servicio web para backend FastAPI
- Base de datos PostgreSQL
- Servicio Redis
- Configuración de entorno para producción
- Variables de entorno seguras

### Requisitos de Sistema

#### Desarrollo
- Python 3.11+
- Node.js 18+
- Docker y Docker Compose
- 4GB RAM mínimo
- 10GB disco disponible

#### Producción
- Python 3.11+
- Node.js 18+ (si se construye frontend)
- Docker y Docker Compose
- 8GB RAM recomendado
- 50GB disco para datos y logs
- Conexión de red estable

## Mantenimiento y Escalabilidad

### Backup y Recuperación

El sistema incluye scripts para:
- Backup de base de datos
- Backup de archivos MinIO
- Recuperación de datos
- Importación de datos de ejemplo

### Monitoreo y Logging

- Logging estructurado con niveles (INFO, ERROR, WARNING)
- Registro de tareas Celery y su estado
- Monitoreo de endpoints de salud
- Seguimiento de errores y excepciones

### Escalabilidad

- Horizontal: Múltiples workers Celery
- Vertical: Aumento de recursos en contenedores
- Distribución: Separación de servicios en diferentes servidores
- Carga balanceada: Múltiples instancias backend

### Actualizaciones

El sistema permite actualizaciones con cero tiempo de inactividad mediante:
- Despliegue blue-green
- Migraciones de base de datos controladas
- Testing automatizado
- Rollback automático en fallos