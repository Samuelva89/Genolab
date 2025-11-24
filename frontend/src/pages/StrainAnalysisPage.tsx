import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, Link } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface Analysis {
  id: number;
  analysis_type: string;
  results: any;
  timestamp: string;
  strain_id: number;
  owner_id: number;
}

interface Strain {
  id: number;
  strain_name: string;
  source: string | null;
  organism_id: number;
  organism: {
    id: number;
    name: string;
    genus: string;
    species: string;
  };
}

const StrainAnalysisPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const strainId = parseInt(id || '0');

  const [strain, setStrain] = useState<Strain | null>(null);
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStrainAndAnalyses = async () => {
      if (isNaN(strainId) || strainId === 0) {
        setError("ID de cepa no válido.");
        setLoading(false);
        return;
      }

      try {
        // Fetch strain details
        const strainResponse = await axios.get<Strain>(`${API_BASE_URL}/api/ceparium/strains/${strainId}`);
        setStrain(strainResponse.data);

        // Fetch analyses for the strain
        const analysesResponse = await axios.get<Analysis[]>(`${API_BASE_URL}/api/analysis/strain/${strainId}`);
        setAnalyses(analysesResponse.data);

      } catch (err) {
        if (axios.isAxiosError(err) && err.response?.status === 404) {
          setError('Cepa no encontrada.');
        } else {
          setError('Error al cargar los detalles de la cepa y sus análisis.');
          console.error('Error fetching strain details or analyses:', err);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchStrainAndAnalyses();
  }, [strainId]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const downloadResults = (analysisId: number) => {
    const link = document.createElement('a');
    link.href = `${API_BASE_URL}/api/analysis/${analysisId}/results/download-txt`;
    link.setAttribute('download', `analysis_results_${analysisId}.txt`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return <p>Cargando detalles de la cepa y sus análisis...</p>;
  }

  if (error) {
    return <p style={{ color: 'red' }}>{error}</p>;
  }

  if (!strain) {
    return <p>No se pudo cargar la información de la cepa.</p>;
  }

  return (
    <div>
      <Link to={`/ceparium/organisms/${strain.organism_id}`}>Volver a detalles del organismo</Link>
      <h1>Análisis de la Cepa: {strain.strain_name}</h1>
      <p><strong>Organismo:</strong> {strain.organism.name} ({strain.organism.genus} {strain.organism.species})</p>
      <p><strong>Fuente:</strong> {strain.source || 'N/A'}</p>
      <p><strong>ID de Cepa:</strong> {strain.id}</p>

      <h2>Análisis Realizados</h2>
      {analyses.length === 0 ? (
        <p>No hay análisis asociados a esta cepa.</p>
      ) : (
        <ul className="data-list">
          {analyses.map((analysis) => (
            <li key={analysis.id} className="data-list-item">
              <div>
                <h4><strong>Tipo:</strong> {analysis.analysis_type}</h4>
                <p><strong>Fecha:</strong> {formatDate(analysis.timestamp)}</p>
                <p><strong>ID:</strong> {analysis.id}</p>
                <div className="results-preview">
                  <p><strong>Resultados:</strong></p>
                  <pre>{JSON.stringify(analysis.results, null, 2)}</pre>
                </div>
                <div className="data-list-item-actions">
                  <button
                    className="button-primary"
                    onClick={() => downloadResults(analysis.id)}
                  >
                    Descargar Resultados (.txt)
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default StrainAnalysisPage;