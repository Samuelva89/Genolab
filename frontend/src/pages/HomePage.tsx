import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import BioIcon from '../components/BioIcon';
import { API_BASE_URL } from '../services/api';

interface SummaryStats {
  totalOrganisms: number;
  totalStrains: number;
  totalAnalyses: number;
}

const HomePage: React.FC = () => {
  const [stats, setStats] = useState<SummaryStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null); // Add error state

  useEffect(() => {
    const fetchSummaryStats = async () => {
      setLoading(true);
      setError(null);
      try {
        // Fetch all summary statistics in a single, efficient API call
        const response = await axios.get<SummaryStats>(`${API_BASE_URL}/api/stats/summary`);
        setStats(response.data);
      } catch (err) {
        console.error('Error fetching summary stats:', err);
        setError('No se pudieron cargar las estadísticas. El servidor puede estar desconectado.');
      } finally {
        setLoading(false);
      }
    };

    fetchSummaryStats();
  }, []);

  if (loading) {
    return (
      <div className="bioinformatics-theme">
        <p>Cargando estadísticas del sistema...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bioinformatics-theme">
        <div className="bioinformatics-card error-message">
          <h1>Error</h1>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bioinformatics-theme fade-in-up">
      <div className="bioinformatics-card">
        <h1 className="welcome-title">
          <BioIcon type="dna" className="sidebar-icon pulse is3d" /> Bienvenido a GENOLAB
        </h1>
        <p className="welcome-subtitle">Plataforma de análisis genómico</p>
        <p className="welcome-description">
          Sistema integral para la gestión de cepas microbianas y análisis bioinformáticos.
        </p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <BioIcon type="dna" className="sidebar-icon is3d" />
          </div>
          <div className="stat-content">
            <h3>Organismos</h3>
            <p className="stat-number">{stats?.totalOrganisms || 0}</p>
            <Link to="/ceparium/organisms" className="stat-link">
              Ver organismos <BioIcon type="file" className="sidebar-icon" />
            </Link>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <BioIcon type="vial" className="sidebar-icon is3d" />
          </div>
          <div className="stat-content">
            <h3>Cepas</h3>
            <p className="stat-number">{stats?.totalStrains || 0}</p>
            <Link to="/ceparium/organisms" className="stat-link">
              Ver cepas <BioIcon type="file" className="sidebar-icon" />
            </Link>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <BioIcon type="chart" className="sidebar-icon is3d" />
          </div>
          <div className="stat-content">
            <h3>Análisis</h3>
            <p className="stat-number">{stats?.totalAnalyses || 0}</p>
            <Link to="/ceparium/analyses" className="stat-link">
              Ver análisis <BioIcon type="file" className="sidebar-icon" />
            </Link>
          </div>
        </div>
      </div>

      <div className="quick-actions">
        <h2>Acciones Rápidas</h2>
        <div className="actions-grid">
          <Link to="/ceparium/organisms/create" className="action-card">
            <BioIcon type="vial" className="sidebar-icon is3d" />
            <h3>Crear Organismo</h3>
            <p>Agregar un nuevo organismo al sistema</p>
          </Link>

          <Link to="/ceparium" className="action-card">
            <BioIcon type="upload" className="sidebar-icon is3d" />
            <h3>Subir Archivo</h3>
            <p>Analizar archivos FASTA, FASTQ, GenBank, etc.</p>
          </Link>

          <Link to="/ceparium/organisms" className="action-card">
            <BioIcon type="microscope" className="sidebar-icon is3d" />
            <h3>Explorar</h3>
            <p>Ver todos los organismos y cepas</p>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
