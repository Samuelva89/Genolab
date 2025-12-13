# Documentación del Proyecto Genolab

Bienvenido a la documentación completa del proyecto Genolab, una plataforma integral para la gestión de cepas microbianas y análisis bioinformáticos.

## Descripción del Proyecto

Genolab es un sistema web desarrollado con FastAPI (backend) y React (frontend) que permite a científicos y técnicos de laboratorio gestionar organismos biológicos, cepas microbianas y realizar análisis genómicos sobre archivos bioinformáticos como FASTA, FASTQ, GenBank y GFF.

## Índice de Documentación

1. [Casos de Uso](./casos_de_uso.md)
   - Descripción detallada de todas las funcionalidades del sistema
   - Actores del sistema y flujos de trabajo

2. [Manual de Usuario](./manual_usuario.md)
   - Guía completa para usuarios del sistema
   - Instrucciones paso a paso para todas las funcionalidades
   - Solución de problemas comunes

3. [Manual Técnico](./manual_tecnico.md)
   - Arquitectura del sistema y tecnologías utilizadas
   - Estructura del proyecto y componentes principales
   - API endpoints y modelos de datos
   - Configuración y despliegue

4. [Manual de Colores y Branding](./manual_colores_branding.md)
   - Identidad visual del sistema
   - Paleta de colores institucionales
   - Guía de aplicación de branding
   - Estilos y tipografía

5. [Documentos Adicionales](./documentos_adicionales.md)
   - Licencia del software
   - Requisitos del sistema
   - Procedimientos de instalación
   - Pruebas y validación
   - Mantenimiento y soporte
   - Seguridad y privacidad
   - Política de backup
   - Versionado

## Estructura del Proyecto

```
documentacion/
├── casos_de_uso.md          # Casos de uso detallados
├── manual_usuario.md        # Manual para usuarios finales
├── manual_tecnico.md        # Documentación técnica para desarrolladores
├── manual_colores_branding.md # Identidad visual y branding
├── documentos_adicionales.md # Documentación complementaria
└── README.md               # Este archivo
```

## Características Principales

- **Gestión de organismos y cepas**: Creación, edición y eliminación de entidades biológicas
- **Análisis bioinformático**: Soporte para archivos FASTA, FASTQ, GenBank y GFF
- **Arquitectura asincrónica**: Procesamiento de archivos en segundo plano con Celery
- **Almacenamiento seguro**: Uso de MinIO para almacenamiento de objetos S3-compatible
- **Interfaz moderna**: Aplicación React con diseño responsive y intuitivo

## Tecnologías Utilizadas

- **Backend**: FastAPI, Python, SQLAlchemy, Celery, Redis
- **Frontend**: React, TypeScript, Vite, Axios
- **Bases de Datos**: PostgreSQL (producción), SQLite (desarrollo)
- **Almacenamiento**: MinIO (compatible con S3)
- **Contenedores**: Docker, Docker Compose
- **Despliegue**: Render

## Autores

Este proyecto fue desarrollado como parte de una solución integral para la gestión de cepas microbianas y análisis genómicos.

## Licencia

Este proyecto se distribuye bajo la licencia MIT - ver el archivo de licencia para más detalles.