// Configuración dinámica para la URL de la API
window.APP_CONFIG = {
  API_URL: window.location.hostname === 'localhost' 
    ? 'http://localhost:8000'  // Para desarrollo local
    : 'http://localhost:8000'  // Para entorno Docker - el backend es mapeado al puerto 8000 del host
};