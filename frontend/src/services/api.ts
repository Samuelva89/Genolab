import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Interceptor para añadir token JWT a todas las solicitudes
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de autenticación
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido, redirigir al login
      localStorage.removeItem('access_token');
      window.location.href = '/login'; // O donde sea que manejes el login
    }
    return Promise.reject(error);
  }
);

// Función para subir archivos a MinIO
export const uploadFile = async (formData: FormData) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/api/analysis/upload/raw`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
};

// Función para obtener la lista de análisis (puedes usarla para listar archivos guardados)
export const getAnalyses = async (strainId: number) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/analysis/strain/${strainId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching analyses:', error);
    throw error;
  }
};