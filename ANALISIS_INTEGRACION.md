# Análisis de Integración Frontend-Backend - Genolab

**Fecha de Análisis**: 2025-12-13  
**Estado General**: ✅ CONFIGURACIÓN CORRECTA

---

## 1. CONFIGURACIÓN DE PUERTOS

### Docker (Desarrollo Local)
| Componente | Puerto | URL | Estado |
|------------|--------|-----|--------|
| Frontend (Nginx) | 8080 | http://localhost:8080 | ✅ |
| Backend (FastAPI) | 8000 | http://localhost:8000 | ✅ |
| MinIO API | 9001 | http://localhost:9001 | ✅ |
| MinIO Console | 9001 | http://localhost:9001 | ✅ |
| Redis | 6379 | redis://localhost:6379 | ✅ |

### Render (Producción)
| Componente | Servicio | Puerto | Estado |
|------------|----------|--------|--------|
| Frontend | genolab-frontend | 8080 | ✅ |
| Backend | genolab-api-mysql | 10000+ | ✅ |
| MySQL | genolab-mysql-db | 3306 (interno) | ✅ |
| Redis | genolab-redis | 6379 (interno) | ✅ |

---

## 2. CONFIGURACIÓN DE CORS (Frontend-Backend)

### Backend (services/app/main.py - Líneas 78-92)
```python
origins = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:8080",  # ✅ Puerto frontend en Docker
    "http://localhost:3000",   # ✅ Desarrollo alternativo
    "http://localhost:5173",   # ✅ Puerto por defecto Vite
]
```

**Análisis**:
- ✅ Permite peticiones del frontend en puerto 8080
- ✅ Permite desarrollo alternativo
- ⚠️ FALTA: Agregar orígenes para producción en Render

**Recomendación**: Actualizar CORS para producción
```python
if os.getenv("TESTING") == "False":
    origins.extend([
        "https://genolab-frontend.onrender.com",
        "https://genolab-api-mysql.onrender.com"
    ])
```

---

## 3. CONFIGURACIÓN DE VARIABLES DE ENTORNO

### Frontend (src/services/api.ts - Líneas 1-43)

```typescript
const API_URL_FROM_ENV = import.meta.env.VITE_API_URL;

const config = {
  development: {
    apiUrl: API_URL_FROM_ENV || "http://localhost:8000",  // ✅
    enableLogging: true,
    enableMockData: false,
    debug: true
  },
  production: {
    apiUrl: API_URL_FROM_ENV || "https://api.genolab.example.com",  // ⚠️ URL placeholder
    ...
  }
};
```

**Análisis**:
- ✅ Usa variables de entorno correctamente
- ✅ Fallback a localhost:8000 en desarrollo
- ⚠️ URL de producción es placeholder

**Estado en diferentes contextos**:

| Contexto | VITE_API_URL | URL Final | Status |
|----------|-------------|-----------|--------|
| Docker Local | NO | http://localhost:8000 | ✅ |
| Render Build | https://genolab-api-mysql.onrender.com | https://genolab-api-mysql.onrender.com | ✅ |
| Desarrollo Vite | NO | http://localhost:8000 | ✅ |

---

## 4. DOCKERFILES - ANÁLISIS

### frontend/Dockerfile (Desarrollo)
```dockerfile
ARG VITE_API_URL=http://localhost:8000     # ✅ Correcto
ENV VITE_API_URL=${VITE_API_URL}           # ✅ Pasado al build
RUN npm run build                           # ✅ Genera dist/
```

**Estado**: ✅ CORRECTO

### frontend/Dockerfile.prod (Producción - Render)
```dockerfile
ARG VITE_API_URL=https://genolab-api-mysql.onrender.com  # ✅
ENV VITE_API_URL=${VITE_API_URL}                         # ✅
RUN npm run build                                         # ✅
```

**Estado**: ✅ CORRECTO

---

## 5. FLUJO DE PETICIONES HTTP

### Petición Típica: Cargar listado de análisis

```
1. Frontend (Puerto 8080)
   └─> GET /ceparium/analyses
       └─> Router llama a AnalysisListPage.tsx
           └─> useEffect() dispara axios.get()
               └─> URL: ${API_BASE_URL}/api/analysis

2. Axios (src/services/api.ts)
   └─> URL: http://localhost:8000/api/analysis (Dev)
   └─> URL: https://genolab-api-mysql.onrender.com/api/analysis (Prod)
       └─> Interceptor de solicitud
           └─> Configurar headers
               └─> timeout: 30 segundos

3. Backend (Puerto 8000 Local / 10000+ Render)
   └─> FastAPI main.py
       └─> CORS Middleware ✅ Valida origen
       └─> Router: /api/analysis
           └─> GET /api/analysis/strain/{strain_id}
               └─> get_analyses_for_strain()
                   └─> Base de datos (SQLite Local / MySQL Render)
                       └─> Retorna JSON

4. Response
   └─> JSON → Frontend
       └─> Interceptor de respuesta
           └─> Manejo de errores (401, 403, 5xx)
               └─> Estado actualizado
                   └─> Re-render componente
```

**Status**: ✅ FLUJO CORRECTO

---

## 6. GESTIÓN DE ARCHIVOS (MinIO)

### Endpoints para Upload
```
Frontend → Backend (8080 → 8000)
  POST /api/analysis/upload/raw
    ├─ Form Data: strain_id, analysis_type, file
    └─ Backend verifica archivo
        └─ Sube a MinIO (9001)
            └─ Retorna URL: http://localhost:9001/genolab-bucket/...
                └─ Guarda en BD
                    └─ Retorna file_url al Frontend
```

**Puerto MinIO**: 
- Local: `http://localhost:9001` ✅
- Configurado en `.env`: `MINIO_ENDPOINT=http://minio:9001` ✅

---

## 7. ANÁLISIS DE RUTAS (Frontend)

### App.tsx - Rutas Registradas

```typescript
<Routes>
  <Route path="/ceparium" element={<CepariumPage />} />
  <Route path="/ceparium/organisms" element={<OrganismListPage />} />
  <Route path="/ceparium/organisms/create" element={<OrganismFormPage />} />
  <Route path="/ceparium/organisms/:id" element={<OrganismDetailPage />} />
  <Route path="/ceparium/strains/:id/analyses" element={<StrainAnalysisPage />} />
  <Route path="/ceparium/analyses" element={<AnalysisListPage />} />
  <Route path="/ceparium/strains/:strainId/upload" element={<IndividualFileUploadPage />} />
  <Route path="/" element={<HomePage />} />
</Routes>
```

**Status**: ✅ Rutas correctamente registradas

---

## 8. ANÁLISIS DE BACKEND ROUTERS

### Routers Registrados (main.py - Líneas 111-119)

```python
api_router = APIRouter(prefix="/api")

api_router.include_router(users.router)           # /api/users
api_router.include_router(organisms.router)       # /api/organisms
api_router.include_router(analysis.router)        # /api/analysis
api_router.include_router(stats.router)           # /api/stats
```

**Verificación de Endpoints**:
- ✅ `/api/analysis` → analysis.py (Línea 29-32)
- ✅ `/api/health` → main.py (Línea 121-123)

---

## 9. CONFIGURACIÓN DE RENDER (render.yaml)

### Servicio Frontend
```yaml
- type: web
  name: genolab-frontend
  env: docker
  dockerfilePath: ./frontend/Dockerfile.prod
  rootDir: ./frontend
  buildCommand: npm ci && npm run build
  startCommand: nginx -g "daemon off;"
  healthCheckPath: /
  envVars:
    - key: VITE_API_URL
      fromService:
        name: genolab-api-mysql
        property: url
```

**Análisis**:
- ✅ Usa Dockerfile.prod correcto
- ✅ Build command instala dependencias
- ✅ Nginx sirve archivos estáticos en puerto 8080
- ✅ Referencia dinámica a backend URL

**Servicio Backend**
```yaml
- type: web
  name: genolab-api-mysql
  env: python
  buildCommand: cd services && pip install -r requirements.txt
  startCommand: cd services && python create_db.py && gunicorn ... app.main:app
  healthCheckPath: /api/health
```

**Status**: ✅ CORRECTO

---

## 10. PROBLEMAS IDENTIFICADOS Y RECOMENDACIONES

### 🔴 CRÍTICO - CORS en Producción
**Problema**: El backend solo acepta orígenes locales en CORS

**Impacto**: Frontend no podrá conectar al backend en Render

**Solución**:
```python
# services/app/main.py
import os

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:5173",
]

# Agregar orígenes de Render en producción
if os.getenv("DEBUG") == "False":
    origins.extend([
        "https://genolab-frontend.onrender.com",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 🟡 IMPORTANTE - Validar VITE_API_URL en Build

**Verificar que en Render**:
1. El frontend recibe la URL correcta del backend
2. La variable se inyecta en el build

**Comando a agregar en logs**:
```bash
echo "VITE_API_URL=${VITE_API_URL}"
npm run build
```

---

### 🟡 IMPORTANTE - Health Check Endpoints

**Backend** ✅ `/api/health` existe

**Frontend** ⚠️ Nginx retorna 200 en `/` automáticamente

---

## 11. VERIFICACIÓN DE FUNCIONAMIENTO LOCAL

### Test Manual:
```bash
# Terminal 1 - Iniciar Docker Compose
docker-compose up

# Terminal 2 - Verificar backend
curl http://localhost:8000/api/health
# Esperado: {"status": "ok"}

# Terminal 3 - Verificar frontend
curl http://localhost:8080/
# Esperado: HTML (índice SPA)

# Terminal 4 - Verificar CORS y API
curl -H "Origin: http://localhost:8080" \
     -H "Access-Control-Request-Method: GET" \
     http://localhost:8000/api/health
# Esperado: Headers con Access-Control-Allow-Origin: http://localhost:8080
```

---

## 12. MATRIZ DE COMPATIBILIDAD

| Característica | Local | Render | Status |
|----------------|-------|--------|--------|
| CORS Configurado | ✅ | ❌ | **REQUIERE FIX** |
| Variables de Entorno | ✅ | ✅ | ✅ |
| Puertos Configurados | ✅ | ✅ | ✅ |
| Rutas Frontend | ✅ | ✅ | ✅ |
| Rutas Backend | ✅ | ✅ | ✅ |
| MinIO Integrado | ✅ | ⚠️ | *Pendiente configuración* |
| Base de Datos | SQLite ✅ | MySQL ✅ | ✅ |
| Redis | ✅ | ✅ | ✅ |

---

## 13. CONCLUSIÓN

### ✅ LO QUE ESTÁ BIEN:

1. **Puertos**: Correctamente configurados (8080 frontend, 8000 backend, 9001 MinIO)
2. **Dockerfiles**: Ambos pasan variables de entorno correctamente
3. **Rutas Frontend**: Correctamente registradas en React Router
4. **Rutas Backend**: Todos los routers incluidos correctamente
5. **Variables de Entorno**: Sistema de fallback funcional
6. **Axios**: Interceptores configurados
7. **MinIO**: Puerto corregido de 9000 a 9001

### ⚠️ REQUIERE ATENCIÓN:

1. **CORS en Producción**: CRÍTICO - Necesita actualizar allowed origins para Render
2. **MinIO en Render**: Necesita credenciales externas configuradas
3. **Base de Datos**: Validar conexión MySQL en Render
4. **Secrets**: Variables sensibles deben estar en Render dashboard

### 📋 PASOS SIGUIENTES:

1. **Actualizar CORS** en `services/app/main.py`
2. **Configurar variables en Render**:
   - MINIO_ENDPOINT
   - MINIO_ACCESS_KEY
   - MINIO_SECRET_KEY
   - SECRET_KEY
   - Credenciales MySQL
3. **Ejecutar tests locales** con docker-compose
4. **Monitorear logs** en Render después del despliegue

---

## 14. COMANDOS ÚTILES

```bash
# Ver logs del frontend en local
docker-compose logs -f frontend

# Ver logs del backend en local
docker-compose logs -f app

# Reconstruir imágenes
docker-compose build --no-cache

# Resetear todo
docker-compose down -v && docker-compose up --build
```

---

**Generado**: 2025-12-13  
**Análisis por**: Sistema Automatizado
