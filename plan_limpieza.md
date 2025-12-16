# Plan de Limpieza del Proyecto Genolab

## FASE 1: Evaluación y Backup (Antes de hacer cambios)

### 1.1. Backup de Archivos Importantes
- [ ] Hacer copia de seguridad de los archivos de backup (backup_*.json)
- [ ] Documentar el estado actual del sistema
- [ ] Crear un branch de backup en el repositorio

### 1.2. Verificación del Sistema
- [ ] Asegurarse de que el sistema actual funciona correctamente
- [ ] Verificar que todas las funcionalidades estén operativas
- [ ] Confirmar que los despliegues a Render funcionan

## FASE 2: Consolidación de Scripts Duplicados

### 2.1. Scripts de Usuario de Prueba
- [ ] Comparar `add_test_user.py` y `setup_test_user.py`
- [ ] Conservar `setup_test_user.py` (más completo y usa SQLAlchemy)
- [ ] Eliminar `add_test_user.py` (usa SQLite directamente)

### 2.2. Scripts de Base de Datos
- [ ] Comparar `recover_database_data.py` con `services/restore_data.py`
- [ ] Conservar `services/restore_data.py` (más completo y parte del sistema principal)
- [ ] Eliminar `recover_database_data.py` (funcionalidad duplicada)

### 2.3. Scripts de Verificación
- [ ] Consolidar `check_*.py` en un único `check_system.py`
- [ ] Conservar funcionalidad esencial de cada script
- [ ] Eliminar scripts redundantes

## FASE 3: Limpieza de Configuraciones Redundantes

### 3.1. Configuraciones de Render
- [ ] Conservar `render.yaml` (versión SQLite)
- [ ] Conservar `render-frontend.yaml` (frontend)
- [ ] Eliminar `mysql_render.yaml` (ya no usamos MySQL)
- [ ] Eliminar `render-simple.yaml` (configuración alternativa)

### 3.2. Scripts de Desarrollo
- [ ] Eliminar `start_dev.bat` y `stop_dev.bat`
- [ ] Agregar comandos equivalentes a `frontend/package.json`
- [ ] Mover otros scripts batch a comandos npm

## FASE 4: Consolidación de Tests

### 4.1. Scripts de Prueba
- [ ] Analizar contenido de cada `test_*.py`
- [ ] Consolidar en un `test_suite.py` o directorio `tests/`
- [ ] Asegurar que toda la funcionalidad de prueba se conserve
- [ ] Eliminar scripts duplicados

## FASE 5: Reorganización de Documentación

### 5.1. Documentación del Sistema
- [ ] Mover `ANALISIS_INTEGRACION.md` y `RESUMEN_INTEGRACION.md` a directorio `docs/`
- [ ] Mantener `README.md` y `DEPLOYMENT_RENDER.md` en raíz
- [ ] Organizar archivos de documentación por tema

## FASE 6: Actualización del package.json

### 6.1. Comandos de Desarrollo
```json
{
  "name": "genolab",
  "scripts": {
    "dev": "docker-compose up --build",
    "dev:down": "docker-compose down",
    "dev:build": "docker-compose build",
    "backend": "cd services && uvicorn app.main:app --reload",
    "frontend": "cd frontend && npm run dev",
    "test": "cd services && python -m pytest",
    "lint": "cd services && python -m flake8 .",
    "backup:data": "cd services && python restore_data.py backup",
    "restore:data": "cd services && python restore_data.py restore"
  },
  "dependencies": {
    "axios": "^1.13.2",
    "react-router-dom": "^7.9.6",
    "zustand": "^5.0.8"
  }
}
```

## FASE 7: Pruebas Post-Limpieza

### 7.1. Validación del Sistema
- [ ] Verificar que Docker Compose funcione correctamente
- [ ] Asegurarse de que los despliegues a Render continúen funcionando
- [ ] Probar todas las funcionalidades principales
- [ ] Verificar que la persistencia de datos funcione

## FASE 8: Documentación Final

### 8.1. Actualizar Documentación
- [ ] Actualizar README.md con la nueva estructura
- [ ] Documentar los nuevos comandos de desarrollo
- [ ] Asegurar que DEPLOYMENT_RENDER.md refleje cambios

## ARCHIVOS A PRESERVAR (No eliminar)
- docker-compose.yml
- Dockerfile
- render.yaml
- render-frontend.yaml
- README.md
- DEPLOYMENT_RENDER.md
- backup_*.json (4 archivos)
- requirements.txt
- frontend/package.json
- frontend/ (todo el directorio)
- services/ (todo el directorio)
- .gitignore

## ARCHIVOS A ELIMINAR (Seguro eliminar)
- add_test_user.py
- recover_database_data.py
- initialize_mysql_db.py
- mysql_render.yaml
- render-simple.yaml
- start_dev.bat
- stop_dev.bat
- (los demás scripts de test y check pueden consolidarse o eliminarse según funcionalidad)

## NOTA IMPORTANTE
Antes de ejecutar este plan:
1. Hacer commit de todos los cambios actuales
2. Crear un branch de backup
3. Asegurarse de que el sistema funcione antes de iniciar
4. Proceder paso a paso y probar cada cambio
5. Si algo falla, revertir al estado anterior y ajustar el plan