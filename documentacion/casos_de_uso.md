# Documentación de Casos de Uso - Genolab

## Descripción General

Genolab es una plataforma integral para la gestión de cepas microbianas y análisis bioinformáticos. El sistema permite a los usuarios gestionar organismos, cepas, y realizar análisis genómicos sobre archivos bioinformáticos como FASTA, FASTQ, GenBank y GFF.

## Actores del Sistema

- **Administrador**: Usuario con permisos especiales para gestionar el sistema
- **Científico/Bioinformático**: Usuario principal que realiza análisis genómicos
- **Técnico de Laboratorio**: Usuario que gestiona cepas y organismos
- **Sistema**: Componentes como Celery, MinIO y la base de datos

## Casos de Uso Detallados

### 1. Gestión de Organismos

**ID:** UC-001  
**Nombre:** Gestionar Organismos  
**Descripción:** Permite al usuario crear, leer, actualizar y eliminar información sobre organismos biológicos  
**Actor Principal:** Científico/Bioinformático, Técnico de Laboratorio  
**Precondiciones:** El usuario debe tener acceso al sistema  
**Flujo Básico:**
1. El usuario accede al panel de organismos
2. El sistema muestra la lista de organismos existentes
3. El usuario puede:
   - Crear un nuevo organismo (nombre, género, especie)
   - Ver detalles de un organismo específico
   - Editar información de un organismo
   - Eliminar un organismo (si no tiene cepas asociadas)

**Flujo Alternativo A:** Intento de eliminar organismo con cepas asociadas
- Sistema muestra mensaje de error indicando la dependencia

### 2. Gestión de Cepas

**ID:** UC-002  
**Nombre:** Gestionar Cepas  
**Descripción:** Permite al usuario crear, leer, actualizar y eliminar cepas microbianas  
**Actor Principal:** Técnico de Laboratorio, Científico  
**Precondiciones:** Existencia de organismos en el sistema  
**Flujo Básico:**
1. El usuario selecciona un organismo
2. El sistema muestra las cepas pertenecientes a ese organismo
3. El usuario puede:
   - Crear una nueva cepa (nombre, fuente, organismo padre)
   - Ver detalles de una cepa específica
   - Editar información de una cepa
   - Eliminar una cepa (si no tiene análisis asociados)

### 3. Subida de Archivos para Análisis

**ID:** UC-003  
**Nombre:** Subir Archivos para Análisis Genómicos  
**Descripción:** Permite al usuario subir archivos bioinformáticos para procesamiento  
**Actor Principal:** Científico/Bioinformático  
**Precondiciones:** El usuario debe haber seleccionado una cepa  
**Flujo Básico:**
1. El usuario selecciona una cepa específica
2. El usuario elige tipo de análisis (FASTA, FASTQ, GenBank, GFF)
3. El usuario sube el archivo correspondiente
4. El sistema valida la extensión del archivo
5. El sistema almacena el archivo en MinIO
6. El sistema crea una tarea asincrónica para procesamiento
7. El sistema devuelve ID de tarea para seguimiento

**Flujo Alternativo A:** Archivo con extensión no válida
- Sistema rechaza la subida y muestra mensaje de error

**Flujo Alternativo B:** Error en procesamiento
- Sistema registra error y notifica al usuario

### 4. Análisis de Archivos FASTA

**ID:** UC-004  
**Nombre:** Conteo y Análisis de Secuencias FASTA  
**Descripción:** Realiza análisis de conteo y contenido GC en archivos FASTA  
**Actor Principal:** Sistema (Tarea Celery), Científico  
**Precondiciones:** Archivo FASTA subido exitosamente  
**Flujo Básico:**
1. Tarea Celery procesa archivo desde MinIO
2. Sistema cuenta secuencias en el archivo
3. Sistema calcula contenido GC promedio
4. Sistema almacena resultados en base de datos
5. Usuario puede consultar resultados

### 5. Análisis de Archivos FASTQ

**ID:** UC-005  
**Nombre:** Análisis de Calidad FASTQ  
**Descripción:** Realiza análisis de calidad y estadísticas en archivos FASTQ  
**Actor Principal:** Sistema (Tarea Celery), Científico  
**Precondiciones:** Archivo FASTQ subido exitosamente  
**Flujo Básico:**
1. Tarea Celery procesa archivo desde MinIO
2. Sistema calcula estadísticas de calidad (longitud promedio, calidad promedio)
3. Sistema almacena resultados en base de datos
4. Usuario puede consultar resultados

### 6. Análisis de Archivos GenBank

**ID:** UC-006  
**Nombre:** Análisis de Archivos GenBank  
**Descripción:** Extrae estadísticas y anotaciones de archivos GenBank  
**Actor Principal:** Sistema (Tarea Celery), Científico  
**Precondiciones:** Archivo GenBank subido exitosamente  
**Flujo Básico:**
1. Tarea Celery procesa archivo desde MinIO
2. Sistema extrae información de anotaciones
3. Sistema cuenta features y estadísticas
4. Sistema almacena resultados en base de datos
5. Usuario puede consultar resultados

### 7. Análisis de Archivos GFF

**ID:** UC-007  
**Nombre:** Análisis de Archivos GFF  
**Descripción:** Cuenta tipos de features en archivos GFF  
**Actor Principal:** Sistema (Tarea Celery), Científico  
**Precondiciones:** Archivo GFF subido exitosamente  
**Flujo Básico:**
1. Tarea Celery procesa archivo desde MinIO
2. Sistema identifica y cuenta tipos de features
3. Sistema almacena resultados en base de datos
4. Usuario puede consultar resultados

### 8. Seguimiento de Tareas Asincrónicas

**ID:** UC-008  
**Nombre:** Seguimiento de Procesamiento  
**Descripción:** Permite al usuario monitorear el estado de análisis asincrónicos  
**Actor Principal:** Científico/Bioinformático  
**Precondiciones:** Tarea de análisis iniciada  
**Flujo Básico:**
1. Usuario obtiene ID de tarea después de subida
2. Usuario consulta estado de tarea vía API
3. Sistema devuelve estado (pendiente, procesando, completado, fallido)
4. Usuario puede repetir consulta hasta finalización

### 9. Visualización de Resultados

**ID:** UC-009  
**Nombre:** Consultar y Descargar Resultados  
**Descripción:** Permite al usuario ver y descargar resultados de análisis  
**Actor Principal:** Científico/Bioinformático  
**Precondiciones:** Análisis completado exitosamente  
**Flujo Básico:**
1. Usuario accede a resultados de análisis
2. Sistema muestra resultados en formato estructurado
3. Usuario puede descargar resultados en formato TXT
4. Usuario puede descargar archivo original desde MinIO

### 10. Gestión de Análisis

**ID:** UC-010  
**Nombre:** Gestionar Análisis  
**Descripción:** Permite al usuario ver, filtrar y administrar análisis realizados  
**Actor Principal:** Científico/Bioinformático  
**Precondiciones:** Existencia de análisis en el sistema  
**Flujo Básico:**
1. Usuario accede al panel de análisis
2. Sistema muestra lista de análisis recientes
3. Usuario puede filtrar por cepa, tipo de análisis, fecha
4. Usuario puede ver detalles de análisis específico
5. Usuario puede eliminar análisis (si es necesario)

### 11. Gestión de Usuarios

**ID:** UC-011  
**Nombre:** Gestionar Usuarios  
**Descripción:** Permite la administración de usuarios del sistema  
**Actor Principal:** Administrador  
**Precondiciones:** Usuario administrador autenticado  
**Flujo Básico:**
1. Administrador accede al panel de usuarios
2. Sistema muestra lista de usuarios
3. Administrador puede:
   - Crear nuevo usuario
   - Activar/desactivar usuarios
   - Asignar permisos especiales

### 12. Obtención de Estadísticas del Sistema

**ID:** UC-012  
**Nombre:** Visualizar Estadísticas  
**Descripción:** Proporciona métricas generales del sistema  
**Actor Principal:** Todos los usuarios  
**Precondiciones:** Acceso al sistema  
**Flujo Básico:**
1. Usuario accede a página principal o panel de estadísticas
2. Sistema consulta base de datos
3. Sistema muestra:
   - Total de organismos
   - Total de cepas
   - Total de análisis realizados
   - Estadísticas por tipo de análisis