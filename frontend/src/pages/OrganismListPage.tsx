import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Definir la interfaz para un Organism, basada en los schemas del backend
interface Organism {
  id: number;
  name: string;
  genus: string;
  species: string;
}

const OrganismListPage: React.FC = () => {
  const [organisms, setOrganisms] = useState<Organism[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

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

  const handleDelete = async (organismId: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este organismo? Esta acción es irreversible.')) {
      try {
        await axios.delete(`${API_BASE_URL}/api/ceparium/organisms/${organismId}`);
        setOrganisms(organisms.filter((org) => org.id !== organismId));
        setError(null); // Limpiar errores previos si la eliminación fue exitosa
      } catch (err) {
        setError('Error al eliminar el organismo. Asegúrese de que no tiene cepas asociadas.');
        console.error('Error deleting organism:', err);
      }
    }
  };


  if (loading) {
    return <p>Cargando organismos...</p>;
  }

  if (error) {
    return <p style={{ color: 'red' }}>{error}</p>;
  }

  return (
    <div>
      <h1>Listado de Organismos</h1>
      <Link to="/ceparium/organisms/create">
        <button className="button-primary">Crear Nuevo Organismo</button>
      </Link>
      {organisms.length === 0 ? (
        <p>No hay organismos registrados.</p>
      ) : (
        <ul className="data-list">
          {organisms.map((organism) => (
            <li key={organism.id} className="data-list-item">
              <Link to={`/ceparium/organisms/${organism.id}`}>
                {organism.name} ({organism.genus} {organism.species})
              </Link>
              <div className="data-list-item-actions">
                <Link to={`/ceparium/organisms/${organism.id}/edit`}>
                  <button className="button-primary">Editar</button>
                </Link>
                <button className="button-danger" onClick={() => handleDelete(organism.id)}>Eliminar</button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default OrganismListPage;