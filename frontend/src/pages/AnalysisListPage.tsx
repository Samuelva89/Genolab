import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import BioIcon from '../components/BioIcon';
import AnalysisChart from '../components/AnalysisChart';
import AnalysisResultDisplay from '../components/AnalysisResultDisplay';
import { API_BASE_URL } from '../services/api';
import axios from 'axios';

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

const AnalysisListPage: React.FC = () => {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Cargar análisis reales de la API
    const fetchAnalyses = async () => {
      try {
        // Intentamos obtener análisis de cepas
        const strainsResponse = await axios.get<Strain[]>(`${API_BASE_URL}/api/ceparium/strains/`);
        const allStrains = strainsResponse.data;

        const allAnalyses: Analysis[] = [];

        for (const strain of allStrains) {
          try {
            const analysesResponse = await axios.get<Analysis[]>(`${API_BASE_URL}/api/analysis/strain/${strain.id}`);
            // Filtrar solo análisis con datos valiosos (excluir raw_file)
            const filteredAnalyses = analysesResponse.data.filter(analysis => analysis.analysis_type !== 'raw_file');

            // Añadir información adicional del cepa y organismo al análisis
            const analysesWithStrainInfo = filteredAnalyses.map(analysis => ({
              ...analysis,
              strain: {
                ...strain,
                organism: strain.organism
              }
            }));
            allAnalyses.push(...analysesWithStrainInfo);
          } catch (err) {
            console.log(`No se encontraron análisis para la cepa ${strain.id}`);
          }
        }

        if (allAnalyses.length > 0) {
          setAnalyses(allAnalyses);
        } else {
          // Si no hay análisis reales, intentamos obtenerlos directamente
          try {
            const allAnalysesResponse = await axios.get<Analysis[]>(`${API_BASE_URL}/api/analysis/analyses`);
            // Filtrar raw_file también aquí
            const filteredAnalyses = allAnalysesResponse.data.filter(analysis => analysis.analysis_type !== 'raw_file');
            setAnalyses(filteredAnalyses);
          } catch (analysesErr) {
            console.log('Error obteniendo análisis directos');
            setAnalyses([]);
          }
        }
      } catch (strainsErr) {
        // Si hay error con cepas, intentamos obtener análisis directamente
        try {
          const allAnalysesResponse = await axios.get<Analysis[]>(`${API_BASE_URL}/api/analysis/analyses`);
          // Filtrar raw_file también aquí
          const filteredAnalyses = allAnalysesResponse.data.filter(analysis => analysis.analysis_type !== 'raw_file');
          setAnalyses(filteredAnalyses);
        } catch (analysesErr) {
          console.log('Error obteniendo análisis directos o cepas');
          setError('No se encontraron análisis en la base de datos');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyses();
  }, []);

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
    return <div className="bioinformatics-theme"><p>Cargando análisis...</p></div>;
  }

  if (error) {
    return <div className="bioinformatics-theme"><p className="error-message">{error}</p></div>;
  }

  // Agrupar análisis por tipo para mostrar gráficas
  const groupedAnalyses = analyses.reduce((acc, analysis) => {
    if (!acc[analysis.analysis_type]) {
      acc[analysis.analysis_type] = [];
    }
    acc[analysis.analysis_type].push(analysis);
    return acc;
  }, {} as Record<string, Analysis[]>);

  return (
    <div className="bioinformatics-theme fade-in-up">
      <div className="bioinformatics-card">
        <Link to="/ceparium">
          <BioIcon type="file" className="sidebar-icon" /> Volver a Ceparium
        </Link>
        <h1><BioIcon type="chart" className="sidebar-icon" is3d /> Análisis - Visualización Centralizada</h1>

        {/* Sección de visualización de gráficas */}
        <div className="analysis-charts-section">
          <h2><BioIcon type="chart" className="sidebar-icon" /> Visualización de Análisis</h2>
          {Object.keys(groupedAnalyses).length === 0 ? (
            <p>No hay análisis disponibles para mostrar.</p>
          ) : (
            Object.entries(groupedAnalyses).map(([analysisType, analysesOfType]) => (
              <div key={analysisType} className="analysis-type-group">
                <h3>{analysisType.replace('_', ' ').toUpperCase()}</h3>
                <div className="analysis-charts-container">
                  {analysesOfType.map((analysis) => (
                    <div key={analysis.id} className="individual-analysis-chart">
                      <h4>Análisis #{analysis.id} - Cepa: {analysis.strain.strain_name}</h4>
                      <div className="chart-wrapper">
                        <AnalysisChart
                          analysisType={analysis.analysis_type}
                          results={analysis.results}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Lista detallada de análisis */}
        <div className="analyses-list-section">
          <h2><BioIcon type="microscope" className="sidebar-icon" /> Detalles de Análisis</h2>
          {analyses.length === 0 ? (
            <p>No hay análisis registrados.</p>
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
                      <AnalysisResultDisplay results={analysis.results} analysis_type={analysis.analysis_type} />
                    </div>

                    <div className="data-list-item-actions">
                      <button
                        className="button-primary"
                        onClick={() => downloadResults(analysis.id)}
                      >
                        <BioIcon type="download" className="sidebar-icon" /> Descargar Resultados (.txt)
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
    </div>
  );
};

export default AnalysisListPage;