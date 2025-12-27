// Configuración dinámica para la URL de la API
window.APP_CONFIG = {
  API_URL: window.location.hostname === 'localhost'
    ? 'http://localhost:8000'  // Para desarrollo local
    : '/api'  // Para entorno Docker - el backend será accesible vía proxy en /api
};