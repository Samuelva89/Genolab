# Manual de Usuario - Genolab

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Primeros Pasos](#primeros-pasos)
3. [Gestión de Organismos](#gestión-de-organismos)
4. [Gestión de Cepas](#gestión-de-cepas)
5. [Análisis de Archivos](#análisis-de-archivos)
6. [Subida de Archivos](#subida-de-archivos)
7. [Visualización de Resultados](#visualización-de-resultados)
8. [Panel de Estadísticas](#panel-de-estadísticas)
9. [Solución de Problemas](#solución-de-problemas)

## Introducción

Genolab es una plataforma web especializada en la gestión de cepas microbianas y el análisis bioinformático. Este sistema permite a científicos y técnicos de laboratorio gestionar organismos biológicos, cepas, y realizar análisis genómicos sobre diferentes tipos de archivos bioinformáticos.

### Características Principales

- Gestión de organismos y cepas microbianas
- Análisis de archivos FASTA, FASTQ, GenBank y GFF
- Procesamiento asincrónico de archivos
- Visualización de resultados
- Estadísticas del sistema

## Primeros Pasos

### Acceso al Sistema

1. Abre tu navegador web preferido (Chrome, Firefox, Safari o Edge)
2. Navega a la dirección URL del sistema Genolab
3. La página principal mostrará las estadísticas generales del sistema

### Interfaz de Usuario

La interfaz de Genolab está construida con React y consta de:
- **Barra de Navegación Lateral**: Acceso rápido a todas las funciones del sistema
- **Panel Principal**: Área de trabajo donde se muestran los contenidos
- **Iconografía Biomédica**: Iconos 3D que representan diferentes funciones

## Gestión de Organismos

### Ver Organismos

1. Haz clic en "Ceparium" en la barra lateral
2. Selecciona "Organismos" en el menú desplegable
3. Se mostrará una lista de todos los organismos registrados
4. Cada organismo muestra su nombre, género y especie

### Crear Nuevo Organismo

1. En el menú lateral, selecciona "Crear Organismo"
2. Opcionalmente, desde la lista de organismos haz clic en "Crear Nuevo"
3. Completa los siguientes campos:
   - **Nombre**: Nombre común del organismo
   - **Género**: Género taxonómico (ej. Escherichia)
   - **Especie**: Especie taxonómica (ej. coli)
4. Haz clic en "Guardar" para registrar el organismo

### Editar Organismo

1. Desde la lista de organismos, haz clic en el organismo que deseas editar
2. Se abrirá la vista detallada del organismo
3. Haz clic en el botón "Editar"
4. Modifica los campos necesarios
5. Haz clic en "Guardar" para aplicar los cambios

## Gestión de Cepas

### Ver Cepas

1. Ve a "Ceparium" → "Organismos" en el menú lateral
2. Selecciona un organismo específico para ver sus cepas
3. La página mostrará todas las cepas pertenecientes a ese organismo

### Crear Nueva Cepa

1. En el menú lateral, selecciona "Crear Cepa"
2. Opcionalmente, desde la vista de organismo haz clic en "Crear Cepa"
3. Completa los siguientes campos:
   - **Nombre de la Cepa**: Nombre específico de la cepa
   - **Fuente**: Origen de la cepa (ej. Laboratorio, Muestra clínica)
   - **Organismo**: Selecciona el organismo padre de la lista
4. Haz clic en "Guardar" para registrar la cepa

### Ver Análisis de una Cepa

1. Navega a la vista detallada de una cepa específica
2. Haz clic en "Ver Análisis" para acceder a todos los análisis realizados a esta cepa

## Análisis de Archivos

Genolab soporta diferentes tipos de análisis bioinformáticos:

### Análisis FASTA

**Tipos de Análisis:**
- **Conteo de Secuencias**: Cuenta el número total de secuencias en el archivo
- **Contenido GC**: Calcula el porcentaje promedio de contenido GC

**Formatos Soportados:** `.fasta`, `.fa`, `.fas`, `.fna`, `.faa`

### Análisis FASTQ

**Tipos de Análisis:**
- **Estadísticas de Calidad**: Calcula longitud promedio, calidad promedio, etc.

**Formatos Soportados:** `.fastq`, `.fq`

### Análisis GenBank

**Tipos de Análisis:**
- **Extracción de Anotaciones**: Obtiene información de anotaciones y features

**Formatos Soportados:** `.gb`, `.gbk`

### Análisis GFF

**Tipos de Análisis:**
- **Conteo de Features**: Cuenta los diferentes tipos de features

**Formatos Soportados:** `.gff`

## Subida de Archivos

### Proceso General de Subida

1. Navega a "Ceparium" → "Subir Archivo" en el menú lateral
2. Selecciona la cepa a la que asociarás el análisis
3. Elige el tipo de análisis que deseas realizar
4. Selecciona el archivo desde tu computadora
5. Haz clic en "Subir y Analizar"

### Subida Individual

1. Desde la vista de una cepa específica, haz clic en "Subir Archivo"
2. Selecciona el tipo de análisis
3. Elige el archivo desde tu computadora
4. Confirma la subida

### Seguimiento de Análisis

Después de subir un archivo:
1. El sistema te proporciona un ID de tarea
2. Puedes hacer seguimiento del estado de procesamiento
3. Una vez completado, los resultados estarán disponibles en el panel de análisis de la cepa

## Visualización de Resultados

### Ver Resultados Detallados

1. Navega a la sección de análisis de una cepa específica
2. Haz clic en el análisis que deseas ver
3. Se mostrarán los resultados detallados del análisis

### Descargar Resultados

1. En la vista de resultados, busca el botón "Descargar TXT"
2. El archivo se descargará con formato texto legible
3. La descarga incluye todos los resultados del análisis

### Descargar Archivo Original

1. En la vista de análisis, busca el botón "Descargar Archivo"
2. El archivo original subido se descargará desde el almacenamiento seguro

## Panel de Estadísticas

### Estadísticas Generales

La página principal muestra:
- Número total de organismos
- Número total de cepas
- Número total de análisis realizados

### Acciones Rápidas

La página principal incluye accesos directos a:
- Crear nuevo organismo
- Subir archivos para análisis
- Explorar organismos y cepas

## Solución de Problemas

### Problemas Comunes y Soluciones

#### Error en Subida de Archivos
**Síntoma:** El sistema rechaza la subida del archivo
**Solución:** Verifica que la extensión del archivo sea compatible (fasta, fastq, gbk, gff, etc.)

#### Análisis No Completa
**Síntoma:** El estado de la tarea permanece en "Procesando" por mucho tiempo
**Solución:** 
- Verifica que el archivo no esté dañado
- Asegúrate de que el archivo no exceda el tamaño máximo permitido
- Contacta al administrador si el problema persiste

#### No se Muestran Resultados
**Síntoma:** El análisis aparece como completado pero no hay resultados visibles
**Solución:** 
- Verifica el formato del archivo original
- Confirma que el archivo contenga datos válidos para el tipo de análisis seleccionado

### Contacto de Soporte

Si experimentas problemas que no están cubiertos en este manual:
1. Anota el error específico que recibes
2. Guarda el ID de tarea si se trata de un análisis
3. Contacta al equipo de soporte técnico con esta información

## Recomendaciones de Uso

### Buenas Prácticas

1. **Nombre Descriptivo:** Usa nombres claros y descriptivos para organismos y cepas
2. **Organización Jerárquica:** Agrupa cepas por organismo para mejor organización
3. **Archivos Válidos:** Asegúrate de que tus archivos bioinformáticos estén en el formato correcto
4. **Tamaños de Archivo:** No excedas los límites de tamaño especificados
5. **Seguimiento:** Monitorea el estado de tus análisis para asegurar su correcta ejecución

### Seguridad y Privacidad

- El sistema almacena tus archivos de forma segura
- Los resultados son accesibles solo por usuarios autorizados
- Los archivos se mantienen en almacenamiento seguro y redundante