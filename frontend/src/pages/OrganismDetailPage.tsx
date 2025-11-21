import React, { useEffect, useState } from 'react';
import axios, { AxiosError } from 'axios';
import { useParams, Link } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Definir las interfaces para Organism y Strain, basadas en los schemas del backend
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
  const { id } = useParams<{ id: string }>(); // Obtener el ID del organismo de la URL
  const organismId = parseInt(id || '0');

  const [organism, setOrganism] = useState<Organism | null>(null);
  const [strains, setStrains] = useState<Strain[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOrganismDetails = async () => {
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
          setError('Error al cargar los detalles del organismo.');
          console.error('Error fetching organism details or strains:', err);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchOrganismDetails();
  }, [organismId]);

  const handleDeleteStrain = async (strainId: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar esta cepa? Esta acción es irreversible.')) {
      try {
        await axios.delete(`${API_BASE_URL}/api/ceparium/strains/${strainId}`);
        setStrains(strains.filter((s) => s.id !== strainId));
        setError(null); // Limpiar errores previos si la eliminación fue exitosa
      } catch (err) {
        setError('Error al eliminar la cepa.');
        console.error('Error deleting strain:', err);
        // Manejo de errores más específico para AxiosError
        if (axios.isAxiosError(err)) {
          console.error('Axios error:', err.response?.data || err.message);
        }
      }
    }
  };

  if (loading) {
    return <p>Cargando detalles del organismo...</p>;
  }

  if (error) {
    return <p style={{ color: 'red' }}>{error}</p>;
  }

  if (!organism) {
    return <p>No se pudo cargar la información del organismo.</p>;
  }

  return (
    <div>
      <Link to="/ceparium/organisms">Volver al listado de Organismos</Link>
      <h1>Detalles del Organismo: {organism.name}</h1>
      <p><strong>Género:</strong> {organism.genus}</p>
      <p><strong>Especie:</strong> {organism.species}</p>
      <p><strong>ID:</strong> {organism.id}</p>

      <h2>Cepas Asociadas</h2>
      <Link to={`/ceparium/organisms/${organismId}/strains/create`}>
        <button className="button-primary">Añadir Nueva Cepa</button>
      </Link>
      {strains.length === 0 ? (
        <p>No hay cepas asociadas a este organismo.</p>
      ) : (
        <ul className="data-list">
          {strains.map((strain) => (
            <li key={strain.id} className="data-list-item">
              <Link to={`/ceparium/strains/${strain.id}`}>
                <strong>{strain.strain_name}</strong> (Fuente: {strain.source || 'N/A'})
              </Link>
              <div className="data-list-item-actions">
                <button className="button-danger" onClick={() => handleDeleteStrain(strain.id)}>Eliminar</button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default OrganismDetailPage;