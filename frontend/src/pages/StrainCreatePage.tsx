import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import BioIcon from '../components/BioIcon';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Definir la interfaz para un Organism, basada en los schemas del backend
interface Organism {
  id: number;
  name: string;
  genus: string;
  species: string;
}

const StrainCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const [organisms, setOrganisms] = useState<Organism[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedOrganismId, setSelectedOrganismId] = useState<number | "">("");

  useEffect(() => {
    const fetchOrganisms = async () => {
      try {
        const response = await axios.get<Organism[]>(`${API_BASE_URL}/api/ceparium/organisms/`);
        setOrganisms(response.data);
      } catch (err) {
        setError('Error al cargar los organismos.');
        console.error('Error fetching organisms:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchOrganisms();
  }, []);

  const handleSelectOrganism = () => {
    if (selectedOrganismId) {
      navigate(`/ceparium/organisms/${selectedOrganismId}/strains/create`);
    } else {
      setError('Por favor selecciona un organismo.');
    }
  };

  if (loading) {
    return <div className="bioinformatics-theme"><p>Cargando organismos...</p></div>;
  }

  if (error && selectedOrganismId === "") {
    return <div className="bioinformatics-theme"><p className="error-message">{error}</p></div>;
  }

  return (
    <div className="bioinformatics-theme fade-in-up">
      <div className="bioinformatics-card">
        <h1><BioIcon type="vial" className="sidebar-icon" is3d /> Crear Nueva Cepa</h1>
        <p>Primero selecciona el organismo al que deseas asociar la cepa:</p>
        
        <div className="form-group">
          <label htmlFor="organism-select">Seleccionar Organismo:</label>
          <select
            id="organism-select"
            value={selectedOrganismId}
            onChange={(e) => setSelectedOrganismId(e.target.value ? Number(e.target.value) : "")}
            className="form-control"
          >
            <option value="">-- Selecciona un Organismo --</option>
            {organisms.map((organism) => (
              <option key={organism.id} value={organism.id}>
                {organism.name} ({organism.genus} {organism.species})
              </option>
            ))}
          </select>
        </div>

        {error && selectedOrganismId === "" && <p className="error-message">{error}</p>}

        <div className="form-actions">
          <button 
            onClick={handleSelectOrganism} 
            disabled={!selectedOrganismId}
            className="button-primary"
          >
            <BioIcon type="vial" className="sidebar-icon" is3d /> Continuar a Crear Cepa
          </button>
          <button 
            className="button-secondary"
            onClick={() => navigate('/ceparium')}
          >
            <BioIcon type="file" className="sidebar-icon" /> Cancelar
          </button>
        </div>
      </div>
    </div>
  );
};

export default StrainCreatePage;