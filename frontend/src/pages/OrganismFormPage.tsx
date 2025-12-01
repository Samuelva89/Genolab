import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import BioIcon from '../components/BioIcon';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface Organism {
  id?: number; // Opcional para la creación
  name: string;
  genus: string;
  species: string;
}

const OrganismFormPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEditing = id !== undefined;
  const organismId = parseInt(id || '0');

  const [formData, setFormData] = useState<Organism>({
    name: '',
    genus: '',
    species: '',
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    if (isEditing) {
      const fetchOrganism = async () => {
        try {
          const response = await axios.get<Organism>(`${API_BASE_URL}/api/ceparium/organisms/${organismId}`);
          setFormData(response.data);
        } catch (err) {
          setError('Error al cargar el organismo para editar.');
          console.error('Error fetching organism for edit:', err);
        } finally {
          setLoading(false);
        }
      };
      fetchOrganism();
    } else {
      setLoading(false);
    }
  }, [isEditing, organismId]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setIsSubmitting(true);
    try {
      if (isEditing) {
        await axios.put(`${API_BASE_URL}/api/ceparium/organisms/${organismId}`, formData);
      } else {
        await axios.post(`${API_BASE_URL}/api/ceparium/organisms/`, formData);
      }
      // Limpiar el formulario después de guardar exitosamente
      setFormData({ name: '', genus: '', species: '' });
      // Navegar directamente sin usar setTimeout para evitar conflictos
      navigate('/ceparium/organisms');
    } catch (err) {
      setError('Error al guardar el organismo.');
      console.error('Error saving organism:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="bioinformatics-theme">
        <p>Cargando formulario...</p>
      </div>
    );
  }

  return (
    <div className="bioinformatics-theme fade-in-up">
      <div className="bioinformatics-card">
        <h1>
          {isEditing ? (
            <>
              <BioIcon type="flask" className="sidebar-icon" is3d /> Editar Organismo
            </>
          ) : (
            <>
              <BioIcon type="vial" className="sidebar-icon" is3d /> Crear Nuevo Organismo
            </>
          )}
        </h1>

        <form onSubmit={handleSubmit}>
          {error && <p className="error-message">{error}</p>}
          {success && <p className="success-message">{success}</p>}

          <div className="form-group">
            <label htmlFor="name">Nombre:</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              disabled={isSubmitting}
            />
          </div>
          <div className="form-group">
            <label htmlFor="genus">Género:</label>
            <input
              type="text"
              id="genus"
              name="genus"
              value={formData.genus}
              onChange={handleChange}
              required
              disabled={isSubmitting}
            />
          </div>
          <div className="form-group">
            <label htmlFor="species">Especie:</label>
            <input
              type="text"
              id="species"
              name="species"
              value={formData.species}
              onChange={handleChange}
              required
              disabled={isSubmitting}
            />
          </div>
          <div className="form-actions">
            <button type="submit" className="button-primary" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <BioIcon type="upload" className="sidebar-icon" spin /> Guardando...
                </>
              ) : isEditing ? (
                <>
                  <BioIcon type="flask" className="sidebar-icon" is3d /> Actualizar Organismo
                </>
              ) : (
                <>
                  <BioIcon type="vial" className="sidebar-icon" is3d /> Crear Organismo
                </>
              )}
            </button>
            <button type="button" className="button-secondary" onClick={() => navigate('/ceparium/organisms')} disabled={isSubmitting}>
              <BioIcon type="file" className="sidebar-icon" /> Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default OrganismFormPage;