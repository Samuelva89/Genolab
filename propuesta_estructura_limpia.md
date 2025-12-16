# Propuesta de Estructura Limpia para Genolab

## Archivos Esenciales (DEBEN mantenerse)
### Configuración del Sistema
- `docker-compose.yml` - Configuración de contenedores Docker
- `Dockerfile` - Configuración de build para frontend + backend
- `render.yaml` - Configuración de despliegue backend en Render (SQLite)
- `render-frontend.yaml` - Configuración de despliegue frontend en Render

### Documentación Principal
- `README.md` - Documentación principal del proyecto
- `DEPLOYMENT_RENDER.md` - Documentación de despliegue

### Datos y Dependencias
- `backup_*.json` (4 archivos) - Datos de respaldo para restauración
- `requirements.txt` - Dependencias del backend
- `frontend/package.json` - Dependencias del frontend

### Código Principal
- `frontend/` - Directorio completo del frontend
- `services/` - Directorio completo del backend

## Archivos Potencialmente Redundantes (a eliminar)

### Scripts Duplicados
- `add_test_user.py` - Similar a `setup_test_user.py` (eliminar uno)
- `recover_database_data.py` - Similar a `services/restore_data.py` (eliminar)
- `initialize_mysql_db.py` - Solo útil para MySQL, ya usamos SQLite (eliminar)
- Scripts batch (`start_dev.bat`, `stop_dev.bat`) - Reemplazar con comandos npm

### Configuraciones Redundantes
- `mysql_render.yaml` - Versión MySQL del backend (eliminar)
- `render-simple.yaml` - Configuración alternativa de Render (eliminar)

### Scripts de Prueba Duplicados
- `check_*.py` (múltiples) - Consolidar en uno o eliminar
- `test_*.py` (múltiples) - Muchos scripts de prueba que pueden consolidarse
- `test_integration.py` - Similar a otros scripts de test (evaluar)

## Propuesta de Nueva Estructura

### Organización por Funcionalidad
```
Genolab/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── render.yaml
├── render-frontend.yaml
├── .gitignore
├── backup_users.json
├── backup_organisms.json
├── backup_strains.json
├── backup_analyses.json
├── frontend/
│   ├── package.json
│   ├── src/
│   └── ...
├── services/
│   ├── requirements.txt
│   ├── create_db.py
│   ├── restore_data.py
│   └── app/
├── docs/
│   ├── DEPLOYMENT_RENDER.md
│   └── ...
├── scripts/ (nuevo directorio para scripts útiles)
│   ├── setup_test_user.py
│   └── ...
└── tests/ (nuevo directorio para pruebas organizadas)
    ├── integration_tests.py
    └── ...
```

### Mejoras Propuestas
1. Consolidar `add_test_user.py` y `setup_test_user.py` en uno solo
2. Eliminar `recover_database_data.py` ya que `services/restore_data.py` tiene funcionalidad similar
3. Eliminar `initialize_mysql_db.py` ya que se usa SQLite
4. Eliminar archivos de configuración redundantes de Render
5. Reemplazar scripts batch con comandos en package.json
6. Consolidar scripts de verificación en un solo archivo más completo
7. Mover documentación a directorio docs/
8. Organizar scripts de prueba en directorio tests/

## Beneficios de la Nueva Estructura
- Menos archivos redundantes
- Estructura más clara y organizada
- Eliminación de duplicados
- Mejor mantenibilidad
- Documentación organizada
- Scripts de desarrollo más accesibles

## Scripts Consolidados Recomendados
1. **setup_test_user.py** (conservar uno solo)
2. **database_tools.py** (consolidar los scripts de verificación de db)
3. **test_suite.py** (consolidar los scripts de test)

## Comandos de Desarrollo a Agregar a package.json
```json
{
  "scripts": {
    "dev": "docker-compose up --build",
    "dev:down": "docker-compose down",
    "backend": "cd services && uvicorn app.main:app --reload",
    "frontend": "cd frontend && npm run dev",
    "test": "cd services && python -m pytest",
    "lint": "cd services && python -m flake8 ."
  }
}
```

Esta estructura mantendrá todas las funcionalidades existentes pero con menos archivos redundantes y una organización más clara.