# Informe Técnico: Sistema de Análisis Genómico Asíncrono

## 1. Introducción

El presente documento describe la arquitectura y funcionalidad de un sistema de análisis genómico diseñado para procesar archivos bioinformáticos de manera asíncrona. El objetivo principal es proporcionar una plataforma robusta y escalable para la gestión y el análisis de datos genómicos asociados a cepas biológicas, permitiendo a los usuarios cargar archivos y obtener resultados detallados de diversos análisis.

## 2. Flujo General del Análisis

El proceso de análisis se ha diseñado para ser eficiente y no bloqueante, utilizando un sistema de colas de tareas. El flujo se puede resumir en los siguientes pasos:

1.  **Inicio del Análisis (API REST)**:
    *   Un usuario (o una aplicación cliente) envía una solicitud HTTP `POST` a un endpoint específico de análisis (ej., `/analysis/upload/fasta_count`).
    *   La solicitud incluye el `strain_id` (identificador de la cepa biológica a la que se asocia el análisis) y el archivo de datos bioinformáticos (ej., FASTA, FASTQ) como `UploadFile`.
    *   **Validación**: El sistema realiza validaciones iniciales, como la existencia de la `strain_id` y el formato/tamaño del archivo cargado.

2.  **Despacho de Tarea Asíncrona (Celery)**:
    *   En lugar de procesar el archivo inmediatamente, el endpoint de FastAPI despacha la tarea de análisis a una cola de tareas gestionada por Celery. Esto se logra mediante llamadas como `process_fasta_count.delay(...)`.
    *   **Respuesta Inmediata**: La API responde al cliente con un código `202 Accepted` y un `task_id` único. Este `task_id` es crucial para que el cliente pueda monitorear el progreso del análisis.

3.  **Procesamiento Asíncrono (Worker de Celery)**:
    *   Un worker de Celery, ejecutándose en segundo plano, recoge la tarea de la cola.
    *   El worker ejecuta la lógica bioinformática real para el tipo de análisis solicitado (ej., parsear el archivo FASTA, contar secuencias, calcular contenido GC).
    *   **Generación de Resultados**: Una vez completado el análisis, el worker genera los resultados, que suelen ser un diccionario o un objeto JSON serializable.
    *   **Almacenamiento en Base de Datos**: El worker invoca una función CRUD (`crud.create_analysis`) para persistir los resultados del análisis en la base de datos, asociándolos con la `strain_id`, el `analysis_type`, los `results` generados y el `owner_id` del usuario que inició la tarea.

4.  **Almacenamiento de Datos (SQLAlchemy y PostgreSQL/SQLite)**:
    *   La función `crud.create_analysis` interactúa con el modelo `Analysis` de SQLAlchemy.
    *   Se inserta un nuevo registro en la tabla `analyses`, que incluye `id`, `analysis_type`, `results` (como objeto JSON), `timestamp` (fecha y hora de creación), `strain_id` (clave foránea a `strains`) y `owner_id` (clave foránea a `users`).

5.  **Monitoreo y Recuperación de Resultados (API REST)**:
    *   El cliente puede consultar periódicamente el estado de su tarea de análisis utilizando el endpoint `/analysis/tasks/{task_id}`.
    *   Este endpoint consulta la aplicación Celery para obtener el estado actual de la tarea (`PENDING`, `PROGRESS`, `SUCCESS`, `FAILURE`).
    *   Si la tarea ha finalizado con éxito (`SUCCESS`), los resultados del análisis (almacenados en la base de datos y/o en el backend de Celery) son devueltos al cliente.

6.  **Recuperación de Análisis Asociados (API REST)**:
    *   Existe un endpoint (`/analysis/strain/{strain_id}`) que permite recuperar todos los análisis previamente realizados y asociados a una cepa biológica específica.

## 3. Componentes Clave de la Arquitectura

*   **FastAPI**: Framework web para la construcción de la API REST, proporcionando validación de datos y documentación automática (Swagger/OpenAPI).
*   **Celery**: Sistema de colas de tareas distribuidas, fundamental para el procesamiento asíncrono de análisis que pueden ser de larga duración.
*   **SQLAlchemy**: ORM (Object-Relational Mapper) para la interacción con la base de datos, permitiendo definir modelos de datos en Python y realizar operaciones CRUD.
*   **Biopython**: Librería estándar de Python para bioinformática, utilizada para el parseo y manipulación de archivos FASTA, FASTQ y GenBank.
*   **BCBio.GFF**: Extensión de Biopython para el manejo de archivos GFF.
*   **Base de Datos**: Utiliza SQLite para desarrollo y pruebas, y es fácilmente adaptable a PostgreSQL para entornos de producción.

## 4. Identificadores Clave en el Sistema

### `strain_id` (Identificador de Cepa)

*   **Propósito**: Es un identificador numérico único que vincula un análisis directamente a una **cepa biológica** específica dentro del sistema.
*   **Relevancia Bioinformática**: En la investigación genómica, los datos de secuencia y los resultados de análisis siempre deben estar asociados a la entidad biológica de la que provienen. El `strain_id` garantiza esta trazabilidad y contextualización.
*   **Implementación**: Es una clave foránea (`ForeignKey`) en la tabla `analyses` que referencia a la tabla `strains`. Esto impone una integridad referencial, asegurando que cada análisis esté asociado a una cepa válida y existente.

### `owner_id` (Identificador de Propietario/Usuario)

*   **Propósito**: Es un identificador numérico único que asocia un análisis con el **usuario** que lo inició o lo "posee" dentro de la plataforma.
*   **Relevancia en la Gestión de Datos**: Permite la auditoría, el control de acceso (quién puede ver/gestionar qué análisis) y la personalización de la experiencia del usuario (mostrar a cada usuario solo sus propios análisis).
*   **Implementación**: Es una clave foránea (`ForeignKey`) en la tabla `analyses` que referencia a la tabla `users`. El sistema obtiene el `owner_id` del usuario autenticado y lo pasa a la tarea de Celery para su registro.

## 5. Tipos de Análisis Genómicos Implementados

El sistema soporta diversos tipos de análisis, cada uno diseñado para extraer información específica de formatos de archivos bioinformáticos comunes. Los resultados de estos análisis se almacenan de forma flexible en un campo `JSON` en la base de datos.

### 5.1. Conteo de Secuencias FASTA (`fasta_count`)

*   **Archivo de Entrada**: Archivos en formato FASTA (`.fasta`, `.fa`, `.fna`, etc.).
*   **Objetivo del Análisis**: Determinar el número total de secuencias (ADN, ARN o proteínas) presentes en el archivo.
*   **Resultados Típicos**:
    ```json
    {
        "filename": "ejemplo.fasta",
        "sequence_count": 150
    }
    ```
*   **Herramientas Utilizadas**: `Biopython` (`Bio.SeqIO.parse`).

### 5.2. Contenido GC de FASTA (`fasta_gc_content`)

*   **Archivo de Entrada**: Archivos en formato FASTA.
*   **Objetivo del Análisis**: Calcular el porcentaje de bases Guanina (G) y Citosina (C) en relación con el total de bases para cada secuencia, y un promedio general para el archivo.
*   **Resultados Típicos**:
    ```json
    {
        "filename": "genoma.fasta",
        "sequence_count": 5,
        "average_gc_content": 45.72,
        "individual_gc_contents": [42.1, 48.5, 45.0, 47.2, 46.0]
    }
    ```
*   **Herramientas Utilizadas**: `Biopython` y `NumPy` para cálculos estadísticos.

### 5.3. Estadísticas FASTQ (`fastq_stats`)

*   **Archivo de Entrada**: Archivos en formato FASTQ (`.fastq`, `.fq`).
*   **Objetivo del Análisis**: Evaluar la calidad y las características de las lecturas de secuenciación, incluyendo el número de lecturas, sus longitudes y la calidad promedio.
*   **Resultados Típicos**:
    ```json
    {
        "filename": "lecturas.fastq",
        "sequence_count": 100000,
        "avg_sequence_length": 150.2,
        "min_length": 140,
        "max_length": 160,
        "overall_avg_quality": 35.8
    }
    ```
*   **Herramientas Utilizadas**: `Biopython` (`Bio.SeqIO.parse`) y `NumPy`.

### 5.4. Estadísticas GenBank (`genbank_stats`)

*   **Archivo de Entrada**: Archivos en formato GenBank (`.gb`, `.gbk`).
*   **Objetivo del Análisis**: Extraer metadatos y estadísticas clave de un registro GenBank, que es un formato rico en anotaciones.
*   **Resultados Típicos**:
    ```json
    {
        "filename": "plásmido.gbk",
        "sequence_count": 1,
        "main_record_id": "NC_000913",
        "description": "Escherichia coli K-12 MG1655, complete genome",
        "sequence_length": 4641652,
        "feature_count": 4289,
        "molecule_type": "DNA",
        "topology": "circular"
    }
    ```
*   **Herramientas Utilizadas**: `Biopython` (`Bio.SeqIO.parse`).

### 5.5. Estadísticas GFF (`gff_stats`)

*   **Archivo de Entrada**: Archivos en formato GFF (General Feature Format) (`.gff`, `.gff3`).
*   **Objetivo del Análisis**: Contar la frecuencia de diferentes tipos de características genómicas (ej., "gene", "CDS", "exon", "tRNA") anotadas en el archivo.
*   **Resultados Típicos**:
    ```json
    {
        "filename": "anotaciones.gff",
        "feature_counts": {
            "gene": 3500,
            "CDS": 3200,
            "tRNA": 80,
            "rRNA": 20
        }
    }
    ```
*   **Herramientas Utilizadas**: `BCBio.GFF` y `collections.Counter`.

## 6. Flexibilidad y Escalabilidad

*   **Resultados Flexibles (Campo `JSON`)**: La decisión de almacenar los resultados de los análisis en un campo `JSON` en la base de datos (`models.Analysis.results`) es fundamental. Permite que cada tipo de análisis devuelva una estructura de datos única y compleja sin requerir modificaciones en el esquema de la base de datos. Esto facilita la adición de nuevos tipos de análisis o la evolución de los resultados existentes de manera ágil.
*   **Procesamiento Asíncrono (Celery)**: La integración con Celery desacopla el procesamiento intensivo de la API, asegurando que la interfaz de usuario permanezca responsiva. Esto es crucial para análisis bioinformáticos que pueden tardar desde segundos hasta horas, permitiendo que el sistema maneje múltiples tareas concurrentemente y escale horizontalmente añadiendo más workers de Celery.

## 7. Conclusión

Este sistema de análisis genómico representa una solución moderna y eficiente para la gestión y el procesamiento de datos bioinformáticos. Su arquitectura asíncrona, la flexibilidad en el manejo de resultados y la clara contextualización de los análisis mediante `strain_id` y `owner_id` lo convierten en una herramienta potente para la investigación y el desarrollo en el campo de la genómica. La utilización de librerías estándar de la industria como Biopython garantiza la precisión y fiabilidad de los análisis.
