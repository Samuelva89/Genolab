import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import BioIcon from '../components/BioIcon';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface Analysis {
  id: number;
  analysis_type: string;
  results: Record<string, unknown>;
  timestamp: string;
  strain_id: number;
  strain: {
    id: number;
    strain_name: string;
    organism_id: number;
    organism: {
      id: number;
      name: string;
      genus: string;
      species: string;
    };
  };
  owner_id: number;
}

const UserAnalysisPage: React.FC = () => {
  // Usamos ID 1 como usuario predeterminado ya que no hay autenticación
  const userId = 1;
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUserAnalyses = async () => {
      try {
        const response = await axios.get<Analysis[]>(`${API_BASE_URL}/api/analysis/user/${userId}/recent-analyses`);
        setAnalyses(response.data);
      } catch (err) {
        setError('Error al cargar los análisis del usuario.');
        console.error('Error fetching user analyses:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchUserAnalyses();
  }, [userId]);

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

  const downloadOriginalFile = (analysisId: number) => {
    const link = document.createElement('a');
    link.href = `${API_BASE_URL}/api/analysis/${analysisId}/download`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return <div className="bioinformatics-theme"><p>Cargando análisis del usuario...</p></div>;
  }

  if (error) {
    return <div className="bioinformatics-theme"><p className="error-message">{error}</p></div>;
  }

  return (
    <div className="bioinformatics-theme fade-in-up">
      <div className="bioinformatics-card">
        <Link to="/ceparium">
          <BioIcon type="file" className="sidebar-icon" /> Volver a Ceparium
        </Link>
        <h1><BioIcon type="chart" className="sidebar-icon" is3d /> Análisis del Usuario</h1>
        {analyses.length === 0 ? (
          <p>No hay análisis registrados para este usuario.</p>
        ) : (
          <ul className="data-list">
            {analyses.map((analysis) => (
              <li key={analysis.id} className="data-list-item">
                <div>
                  <h4><BioIcon type="microscope" className="sidebar-icon" is3d /> {analysis.analysis_type}</h4>
                  <p><strong>ID:</strong> {analysis.id}</p>
                  <p><strong>Fecha:</strong> {formatDate(analysis.timestamp)}</p>
                  <p><strong>Cepa:</strong> {analysis.strain.strain_name} (ID: {analysis.strain.id})</p>
                  <p><strong>Organismo:</strong> {analysis.strain.organism.name} ({analysis.strain.organism.genus} {analysis.strain.organism.species})</p>
                  <div className="results-preview">
                    <p><strong>Resultados:</strong></p>
                    <pre>{JSON.stringify(analysis.results, null, 2)}</pre>
                  </div>
                  <div className="data-list-item-actions">
                    <button
                      className="button-primary"
                      onClick={() => downloadResults(analysis.id)}
                    >
                      <BioIcon type="download" className="sidebar-icon" /> Descargar Resultados (.txt)
                    </button>
                    <button
                      className="button-primary"
                      onClick={() => downloadOriginalFile(analysis.id)}
                    >
                      <BioIcon type="download" className="sidebar-icon" /> Descargar Archivo Original
                    </button>
                    <Link to={`/ceparium/strains/${analysis.strain_id}/analyses`}>
                      <button className="button-primary">
                        <BioIcon type="chart" className="sidebar-icon" is3d /> Ver Análisis
                      </button>
                    </Link>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default UserAnalysisPage;