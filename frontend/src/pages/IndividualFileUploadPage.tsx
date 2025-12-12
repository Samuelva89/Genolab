import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import FileUploadComponent from '../components/FileUploadComponent';
import AnalysisResultDisplay from '../components/AnalysisResultDisplay';
import { API_BASE_URL } from '../services/api';
import axios from 'axios';

interface Analysis {
  id: number;
  analysis_type: string;
  timestamp: string;
  results: any;
  strain_id: number;
  owner_id: number;
  file_url: string;
}

const IndividualFileUploadPage: React.FC = () => {
  const { strainId } = useParams<{ strainId: string }>();
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (strainId) {
      fetchAnalyses();
    }
  }, [strainId]);

  const fetchAnalyses = async () => {
    try {
      setLoading(true);
      const response = await axios.get<Analysis[]>(`${API_BASE_URL}/api/analysis/strain/${Number(strainId)}`);
      setAnalyses(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching analyses:', err);
      setError('No se pudieron cargar los análisis guardados.');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = () => {
    // Refrescar la lista de análisis después de una subida exitosa
    fetchAnalyses();
  };

  if (!strainId) {
    return (
      <div className="bioinformatics-theme">
        <div className="bioinformatics-card">
          <h1>Error</h1>
          <p>No se proporcionó un ID de cepa válido.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bioinformatics-theme">
      <div className="bioinformatics-card">
        <h1>Subida de Archivos Individuales</h1>
        <p>Sube archivos FASTA, FASTQ, GenBank, GFF u otros formatos biológicos directamente a MinIO sin análisis adicional.</p>

        <div className="file-upload-section">
          <FileUploadComponent
            strainId={Number(strainId)}
            onUploadSuccess={handleUploadSuccess}
          />
        </div>

        <div className="saved-files-section">
          <h2>Archivos guardados</h2>
          {loading ? (
            <p>Cargando archivos guardados...</p>
          ) : error ? (
            <p className="error-message">{error}</p>
          ) : (
            <div>
              {analyses.length > 0 ? (
                <ul className="analysis-list">
                  {analyses
                    .map(analysis => (
                      <li key={analysis.id} className="analysis-item">
                        <div className="analysis-info">
                          <h4>Archivo #{analysis.id}</h4>
                          <p>Tipo: {analysis.analysis_type}</p>
                          <p>Fecha: {new Date(analysis.timestamp).toLocaleString()}</p>
                          <div className="results-preview">
                            <AnalysisResultDisplay results={analysis.results} analysis_type={analysis.analysis_type} />
                          </div>
                        </div>
                      </li>
                    ))}
                </ul>
              ) : (
                <p>No hay archivos guardados para esta cepa.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default IndividualFileUploadPage;