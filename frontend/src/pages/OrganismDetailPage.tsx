import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, Link, useNavigate } from 'react-router-dom';
import BioIcon from '../components/BioIcon';

import { API_BASE_URL } from '../services/api';

interface Organism {
  id: number;
  name: string;
  genus: string;
  species: string;
}

interface Strain {
  id: number;
  strain_name: string;
  source: string | null;
  organism_id: number;
}

const OrganismDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const organismId = parseInt(id || '0');

  const [organism, setOrganism] = useState<Organism | null>(null);
  const [strains, setStrains] = useState<Strain[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOrganismAndStrains = async () => {
      if (isNaN(organismId) || organismId === 0) {
        setError("ID de organismo no válido.");
        setLoading(false);
        return;
      }

      try {
        // Fetch organism details
        const organismResponse = await axios.get<Organism>(`${API_BASE_URL}/api/ceparium/organisms/${organismId}`);
        setOrganism(organismResponse.data);

        // Fetch strains for the organism
        const strainsResponse = await axios.get<Strain[]>(`${API_BASE_URL}/api/ceparium/organisms/${organismId}/strains`);
        setStrains(strainsResponse.data);

      } catch (err) {
        if (axios.isAxiosError(err) && err.response?.status === 404) {
          setError('Organismo no encontrado.');
        } else {
          setError('Error al cargar los detalles del microorganismo y sus cepas.');
          console.error('Error fetching organism details or strains:', err);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchOrganismAndStrains();
  }, [organismId]);

  const handleDelete = async (organismId: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este microorganismo? Esta acción es irreversible.')) {
      try {
        await axios.delete(`${API_BASE_URL}/api/ceparium/organisms/${organismId}`);
        // Mostrar mensaje de éxito y redirigir después de un corto tiempo
        setError(null); // Limpiar errores previos
        // Redirigir a la lista de organismos
        navigate('/ceparium/organisms');
      } catch (err) {
        setError('Error al eliminar el microorganismo. Asegúrese de que no tiene cepas asociadas.');
        console.error('Error deleting organism:', err);
      }
    }
  };

  if (loading) {
    return (
      <div className="bioinformatics-theme">
        <p>Cargando detalles del microorganismo...</p>
      </div>
    );
  }

  if (error) {
    return <div className="bioinformatics-theme"><p className="error-message">{error}</p></div>;
  }

  if (!organism) {
    return <div className="bioinformatics-theme"><p>No se pudo cargar la información del microorganismo.</p></div>;
  }

  return (
    <div className="bioinformatics-theme fade-in-up">
      <div className="bioinformatics-card">
        <Link to="/ceparium/organisms">
          <BioIcon type="file" className="sidebar-icon" /> Volver a lista de microorganismos
        </Link>
        <h1>
          <BioIcon type="dna" className="sidebar-icon" is3d /> Detalles del Microorganismo: {organism.name}
        </h1>
        <div className="organism-info">
          <p><strong>Nombre:</strong> {organism.name}</p>
          <p><strong>Género:</strong> {organism.genus}</p>
          <p><strong>Especie:</strong> {organism.species}</p>
          <p><strong>ID:</strong> {organism.id}</p>
        </div>

        <div className="form-actions">
          <Link to={`/ceparium/organisms/${organismId}/edit`}>
            <button className="button-primary">
              <BioIcon type="flask" className="sidebar-icon" is3d /> Editar Microorganismo
            </button>
          </Link>
                      <button className="button-danger" onClick={() => handleDelete(organismId)}>
                        <BioIcon type="file" className="sidebar-icon" is3d /> Eliminar Microorganismo
                      </button>        </div>

        <h2><BioIcon type="vial" className="sidebar-icon" is3d /> Cepas Asociadas</h2>
        {strains.length === 0 ? (
          <p>No hay cepas asociadas a este microorganismo.</p>
        ) : (
          <ul className="data-list">
            {strains.map((strain) => (
              <li key={strain.id} className="data-list-item">
                <Link to={`/ceparium/strains/${strain.id}/analyses`}>
                  <BioIcon type="microscope" className="sidebar-icon" is3d />
                  {strain.strain_name} (ID: {strain.id})
                </Link>
                <div className="data-list-item-actions">
                  <Link to={`/ceparium/strains/${strain.id}/analyses`}>
                    <button className="button-primary">
                      <BioIcon type="chart" className="sidebar-icon" is3d /> Ver Análisis
                    </button>
                  </Link>
                </div>
              </li>
            ))}
          </ul>
        )}

        <div className="form-actions">
          <Link to={`/ceparium/organisms/${organismId}/strains/create`}>
            <button className="button-primary">
              <BioIcon type="vial" className="sidebar-icon" is3d /> Crear Nueva Cepa
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default OrganismDetailPage;