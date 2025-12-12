import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import BioIcon from '../components/BioIcon';
import { API_BASE_URL } from '../services/api';
import '../Styles/CepariumUploadStyles.css';

// Definir la interfaz para un Organism, basada en los schemas del backend
interface Organism {
  id: number;
  name: string;
  genus: string;
  species: string;
}

// Interfaz para la Cepa
interface Strain {
  id: number;
  strain_name: string;
  source: string | null;
  organism_id: number;
}

// Interfaz para el estado de la tarea de Celery
interface TaskStatus {
  status: string;
  progress?: number;
  state: "PENDING" | "SUCCESS" | "FAILURE" | string;
  result?: unknown; // Usar unknown es más seguro que any
  error?: string;
}

// Función auxiliar para formatear los resultados del análisis
const formatAnalysisResult = (result: unknown, analysisType: string) => {
  if (result === null || result === undefined) {
    return <p>No hay resultados disponibles.</p>;
  }

  // Asumimos que los resultados son objetos para la mayoría de los casos
  if (typeof result !== "object" || result === null) {
    return <p>Resultados: {String(result)}</p>;
  }

  const resultObj = result as Record<string, unknown>; // Casteamos a un tipo más flexible para acceder a propiedades

  switch (analysisType) {
    case "fasta_count":
      if ("count" in resultObj && typeof resultObj.count === "number") {
        return (
          <p>
            Conteo de secuencias FASTA: <strong>{resultObj.count}</strong>
          </p>
        );
      }
      break;
    case "fasta_gc_content":
      if (
        "gc_content" in resultObj &&
        typeof resultObj.gc_content === "number"
      ) {
        return (
          <p>
            Contenido GC en FASTA:{" "}
            <strong>{(resultObj.gc_content * 100).toFixed(2)}%</strong>
          </p>
        );
      }
      break;
    case "fastq_stats":
    case "genbank_stats":
    case "gff_stats":
      // Para estadísticas más generales, mostramos una lista
      return (
        <ul>
          {Object.entries(resultObj).map(([key, value]) => (
            <li key={key}>
              {key.replace(/_/g, " ")}: <strong>{String(value)}</strong>
            </li>
          ))}
        </ul>
      );
    default:
      // Si no hay un formato específico, o si el tipo no coincide, mostramos el JSON
      break;
  }

  // Fallback si no se pudo formatear de forma específica
  if (typeof result === 'object' && result !== null) {
    return (
      <div>
        <p>Resultados detallados:</p>
        <pre>{JSON.stringify(result, null, 2)}</pre>
      </div>
    );
  }

  return <p>Resultados: {String(result)}</p>;
};

const CepariumPage: React.FC = () => {
  const [organisms, setOrganisms] = useState<Organism[]>([]);
  const [loadingOrganisms, setLoadingOrganisms] = useState<boolean>(true);
  const [errorOrganisms, setErrorOrganisms] = useState<string | null>(null);

  const [strains, setStrains] = useState<Strain[]>([]);
  const [loadingStrains, setLoadingStrains] = useState<boolean>(true);
  const [errorStrains, setErrorStrains] = useState<string | null>(null);
  const [selectedStrainId, setSelectedStrainId] = useState<number | "">("");
  const [selectedAnalysisType, setSelectedAnalysisType] =
    useState<string>("fasta_count");

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null); // Para guardar el ID de la tarea de Celery
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null); // Para guardar el estado de la tarea

  // Fetch Organisms
  useEffect(() => {
    const fetchOrganisms = async () => {
      try {
        const response = await axios.get<Organism[]>(
          `${API_BASE_URL}/api/ceparium/organisms/`
        );
        setOrganisms(response.data);
      } catch (err) {
        setErrorOrganisms("Error al cargar los organismos.");
        console.error("Error fetching organisms:", err);
      } finally {
        setLoadingOrganisms(false);
      }
    };

    fetchOrganisms();
  }, []);

  // Fetch Strains
  useEffect(() => {
    const fetchStrains = async () => {
      try {
        // Asumiendo que existe un endpoint para listar todas las cepas
        const response = await axios.get<Strain[]>(
          `${API_BASE_URL}/api/ceparium/strains/`
        );
        setStrains(response.data);
      } catch (err) {
        setErrorStrains("Error al cargar las cepas.");
        console.error("Error fetching strains:", err);
      } finally {
        setLoadingStrains(false);
      }
    };

    fetchStrains();
  }, []);

  // Polling para el estado de la tarea de Celery
  useEffect(() => {
    let intervalId: NodeJS.Timeout;
    if (taskId) {
      intervalId = setInterval(async () => {
        try {
          const response = await axios.get(
            `${API_BASE_URL}/api/analysis/tasks/${taskId}`
          );
          setTaskStatus(response.data);
          if (
            response.data.state === "SUCCESS" ||
            response.data.state === "FAILURE"
          ) {
            clearInterval(intervalId);
          }
        } catch (err) {
          console.error("Error fetching task status:", err);
          clearInterval(intervalId);
        }
      }, 3000); // Poll cada 3 segundos
    }
    return () => clearInterval(intervalId);
  }, [taskId]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
      setUploadError(null);
      setUploadSuccess(null);
      setTaskId(null); // Limpiar cualquier tarea anterior
      setTaskStatus(null);
    } else {
      setSelectedFile(null);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setUploadError("Por favor, selecciona un archivo para subir.");
      return;
    }
    if (!selectedStrainId) {
      setUploadError("Por favor, selecciona una cepa.");
      return;
    }

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);
    setTaskId(null);
    setTaskStatus(null);

    try {
      // Si es análisis tipo raw_file, usar endpoint diferente
      let response;
      if (selectedAnalysisType === 'raw_file') {
        // Endpoint para subir archivos sin análisis
        const rawFormData = new FormData();
        rawFormData.append("strain_id", String(selectedStrainId));
        rawFormData.append("file", selectedFile);
        rawFormData.append("analysis_type", "raw_file");

        response = await axios.post(
          `${API_BASE_URL}/api/analysis/upload/raw`,
          rawFormData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );

        // Mostrar la URL directa del archivo subido
        setUploadSuccess(
          `Archivo subido exitosamente. URL de acceso: ${response.data.file_url}`
        );
      } else {
        // Endpoint para análisis con procesamiento
        const formData = new FormData();
        formData.append("strain_id", String(selectedStrainId));
        formData.append("file", selectedFile);

        response = await axios.post(
          `${API_BASE_URL}/api/analysis/upload/${selectedAnalysisType}`,
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );
        // Para análisis con tareas, guardar el ID de la tarea
        setTaskId(response.data.task_id);
        setUploadSuccess(response.data.message || "Archivo subido con éxito.");
      }
    } catch (error) {
      const errorMessage =
        axios.isAxiosError(error) && error.response
          ? error.response.data?.detail || "Error al subir el archivo."
          : "Error al subir el archivo.";
      setUploadError(errorMessage);
      console.error("Error uploading file:", error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="ceparium-upload-page fade-in-up">
      <div className="ceparium-upload-container">
        <h1 className="ceparium-upload-title">
          <BioIcon type="dna" className="sidebar-icon" pulse is3d /> Página Ceparium <BioIcon type="microscope" className="sidebar-icon" spin is3d />
        </h1>

        <div className="ceparium-upload-section">
          <h2>
            <BioIcon type="vial" className="sidebar-icon" /> Visualización de Organismos
          </h2>
          {loadingOrganisms ? (
            <p>Cargando organismos...</p>
          ) : errorOrganisms ? (
            <p className="error-message">{errorOrganisms}</p>
          ) : organisms.length === 0 ? (
            <p>No hay organismos registrados.</p>
          ) : (
            <ul>
              {organisms.map((organism) => (
                <li key={organism.id}>
                  <Link to={`/ceparium/organisms/${organism.id}`}>
                    {organism.name} ({organism.genus} {organism.species})
                  </Link>
                  <Link to={`/ceparium/organisms/${organism.id}/edit`}>
                    <button className="button-primary">Editar</button>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="ceparium-upload-section">
          <h2>
            <BioIcon type="upload" className="sidebar-icon" pulse /> Carga de Archivos
          </h2>
          <div className="upload-form-group">
            <label htmlFor="strain-select">
              <BioIcon type="vial" className="sidebar-icon" /> Seleccionar Cepa:
            </label>
            {loadingStrains ? (
              <p>Cargando cepas...</p>
            ) : errorStrains ? (
              <p className="error-message">{errorStrains}</p>
            ) : (
              <select
                id="strain-select"
                value={selectedStrainId}
                onChange={(e) => setSelectedStrainId(Number(e.target.value))}
                disabled={strains.length === 0}
                className="form-control"
              >
                <option value="">-- Selecciona una Cepa --</option>
                {strains.map((strain) => (
                  <option key={strain.id} value={strain.id}>
                    {strain.strain_name} (Organismo: {strain.organism_id})
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className="upload-form-group">
            <label htmlFor="analysis-type-select">
              <BioIcon type="chart" className="sidebar-icon" /> Tipo de Análisis:
            </label>
            <select
              id="analysis-type-select"
              value={selectedAnalysisType}
              onChange={(e) => setSelectedAnalysisType(e.target.value)}
              className="form-control"
            >
              <option value="fasta_count">Conteo FASTA</option>
              <option value="fasta_gc_content">Contenido GC FASTA</option>
              <option value="fastq_stats">Estadísticas FASTQ</option>
              <option value="genbank_stats">Estadísticas GenBank</option>
              <option value="gff_stats">Estadísticas GFF</option>
              <option value="raw_file">Subir archivo sin análisis</option>
            </select>
          </div>

          <div className="upload-form-group">
            <label htmlFor="file-upload">
              <BioIcon type="file" className="sidebar-icon" /> Seleccionar Archivo:
            </label>
            <input id="file-upload" type="file" onChange={handleFileChange} className="form-control" />
          </div>

          <div className="upload-actions">
            <button
              onClick={handleFileUpload}
              disabled={!selectedFile || !selectedStrainId || uploading}
              className="file-upload-button"
            >
              <BioIcon type="upload" className="sidebar-icon" spin={uploading} />{' '}
              {uploading ? "Subiendo..." : "Subir Archivo"}
            </button>
          </div>

          {selectedFile && (
            <div className="selected-file-info">
              <p>Archivo seleccionado: {selectedFile.name}</p>
            </div>
          )}
          {uploading && (
            <div className="uploading-message">
              <p>Cargando archivo...</p>
            </div>
          )}
          {uploadError && <p className="error-message">{uploadError}</p>}
          {uploadSuccess && (
            <div className="success-message">
              <p>{uploadSuccess}</p>
              {selectedAnalysisType === 'raw_file' && (
                <p className="info-message">
                  El archivo ha sido subido directamente a MinIO sin procesamiento.
                  La URL proporcionada te permite acceder directamente al archivo.
                </p>
              )}
            </div>
          )}
        </div>

        {taskId && (
          <div className="analysis-status-card">
            <h2>
              <BioIcon type="chart" className="sidebar-icon" spin /> Estado de la Tarea de Análisis (ID: {taskId})
            </h2>
            <div className="analysis-status-container">
              {taskStatus ? (
                <div>
                  <p>Estado: {taskStatus.status}</p>
                  {taskStatus.progress !== undefined && (
                    <>
                      <p>Progreso: {taskStatus.progress}%</p>
                      <div className="task-progress-bar">
                        <div
                          className="task-progress"
                          style={{ width: `${taskStatus.progress}%` }}
                        ></div>
                      </div>
                    </>
                  )}
                  {taskStatus.state === "SUCCESS" && taskStatus.result && (
                    <div className="analysis-results">
                      <h3>
                        <BioIcon type="download" className="sidebar-icon" pulse /> Resultados:
                      </h3>
                      {formatAnalysisResult(
                        taskStatus.result,
                        selectedAnalysisType
                      )}
                    </div>
                  )}
                  {taskStatus.state === "FAILURE" && (
                    <p className="task-error">Error: {taskStatus.error}</p>
                  )}
                </div>
              ) : (
                <p>Esperando el estado de la tarea...</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CepariumPage;
