// La URL base se define prioritariamente por la variable de entorno
// Si está disponible, se usa siempre independientemente del entorno
const API_URL_FROM_ENV = import.meta.env.VITE_API_URL;

// Configuración para diferentes entornos
const config = {
  development: {
    apiUrl: API_URL_FROM_ENV || "http://localhost:8000",
    enableLogging: true,
    enableMockData: false,
    debug: true
  },
  production: {
    apiUrl: API_URL_FROM_ENV || "/api",
    enableLogging: false,
    enableMockData: false,
    debug: false
  },
  staging: {
    apiUrl: API_URL_FROM_ENV || "/api",
    enableLogging: true,
    enableMockData: false,
    debug: true
  }
};

// Detectar entorno
const getEnvironment = () => {
  const env = import.meta.env.MODE || 'development';
  return env;
};

// Obtener configuración actual
const currentEnv = getEnvironment();
const appConfig = config[currentEnv] || config.development;

// Exportar configuración
export const API_BASE_URL = appConfig.apiUrl;
export const ENABLE_LOGGING = appConfig.enableLogging;
export const ENABLE_MOCK_DATA = appConfig.enableMockData;
export const IS_DEBUG = appConfig.debug;
export const ENVIRONMENT = currentEnv;

// Función para loggear (solo en desarrollo o si está habilitado)
export const log = (...args: any[]) => {
  if (ENABLE_LOGGING || IS_DEBUG) {
    console.log('[GENOLAB]', ...args);
  }
};

// Función para loggear errores
export const logError = (...args: any[]) => {
  console.error('[GENOLAB ERROR]', ...args);
  // Aquí podrías integrar con servicios de logging como Sentry
};

// Configuración de axios con interceptores
import axios from 'axios';

// Configurar axios con tiempo de espera
axios.defaults.timeout = 30000; // 30 segundos

// Interceptor de solicitud
axios.interceptors.request.use(
  (config) => {
    log('Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    logError('Request error:', error);
    return Promise.reject(error);
  }
);

// Interceptor de respuesta
axios.interceptors.response.use(
  (response) => {
    log('Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    logError('Response error:', error.response?.status, error.response?.data);

    // Manejar errores específicos
    if (error.response?.status === 401) {
      // Token expirado - redirigir a login si se implementa autenticación
      console.warn('Sesión expirada - implementar redirección a login');
    } else if (error.response?.status === 403) {
      console.warn('Acceso denegado - implementar manejo de permisos');
    } else if (error.response?.status >= 500) {
      console.error('Error del servidor - contactar al administrador');
    }

    return Promise.reject(error);
  }
);

export default axios;