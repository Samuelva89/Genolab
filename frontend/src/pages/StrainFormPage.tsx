import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import BioIcon from '../components/BioIcon';

import { API_BASE_URL } from '../services/api';

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
    <div className="bioinformatics-theme fade-in-up">
      <div className="bioinformatics-card">
        <h1><BioIcon type="vial" className="sidebar-icon" is3d /> Crear Nueva Cepa para Organismo ID: {organismId}</h1>

        <form onSubmit={handleSubmit}>
          {error && <p className="error-message">{error}</p>}
          {success && <p className="success-message">{success}</p>}

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
              {isSubmitting ? (
                <>
                  <BioIcon type="upload" className="sidebar-icon" spin /> Creando...
                </>
              ) : (
                <>
                  <BioIcon type="vial" className="sidebar-icon" is3d /> Crear Cepa
                </>
              )}
            </button>
            <button type="button" className="button-secondary" onClick={() => navigate(`/ceparium/organisms/${organismId}`)} disabled={isSubmitting}>
              <BioIcon type="file" className="sidebar-icon" /> Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default StrainFormPage;