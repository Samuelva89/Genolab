import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface StrainCreate {
  strain_name: string;
  source: string;
  organism_id: number;
}

const StrainFormPage: React.FC = () => {
  const { organismId } = useParams<{ organismId: string }>();
  const navigate = useNavigate();
  const organismIdNum = parseInt(organismId || '0');

  const [formData, setFormData] = useState<StrainCreate>({
    strain_name: '',
    source: '',
    organism_id: organismIdNum,
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    // Ensure organismId is valid and update form data
    if (isNaN(organismIdNum) || organismIdNum === 0) {
      setError("ID de organismo no válido.");
    } else {
      setFormData((prev) => ({ ...prev, organism_id: organismIdNum }));
    }
  }, [organismIdNum]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (isNaN(formData.organism_id) || formData.organism_id === 0) {
      setError("Debe asociar la cepa a un organismo válido.");
      return;
    }

    setIsSubmitting(true);
    try {
      await axios.post(`${API_BASE_URL}/api/ceparium/strains/`, formData);
      setSuccess('Cepa creada exitosamente.');
      
      setTimeout(() => {
        navigate(`/ceparium/organisms/${organismId}`); // Redirigir a la página de detalles del organismo
      }, 1500);

    } catch (err) {
      setError('Error al crear la cepa.');
      console.error('Error creating strain:', err);
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <h1>Crear Nueva Cepa para Organismo ID: {organismId}</h1>
      
      <form onSubmit={handleSubmit}>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        {success && <p style={{ color: 'green' }}>{success}</p>}

        <div className="form-group">
          <label htmlFor="strain_name">Nombre de la Cepa:</label>
          <input
            type="text"
            id="strain_name"
            name="strain_name"
            value={formData.strain_name}
            onChange={handleChange}
            required
            disabled={isSubmitting}
          />
        </div>
        <div className="form-group">
          <label htmlFor="source">Fuente:</label>
          <input
            type="text"
            id="source"
            name="source"
            value={formData.source}
            onChange={handleChange}
            disabled={isSubmitting}
          />
        </div>
        <div className="form-actions">
          <button type="submit" className="button-primary" disabled={isSubmitting}>
            {isSubmitting ? 'Creando...' : 'Crear Cepa'}
          </button>
          <button type="button" className="button-secondary" onClick={() => navigate(`/ceparium/organisms/${organismId}`)} disabled={isSubmitting}>
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
};

export default StrainFormPage;