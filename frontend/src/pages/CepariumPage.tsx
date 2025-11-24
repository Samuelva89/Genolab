import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";


const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

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
  name: string;
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
  return (
    <div>
      <p>Resultados detallados (JSON):</p>
      <pre>{JSON.stringify(result, null, 2)}</pre>
    </div>
  );
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

    const formData = new FormData();
    formData.append("strain_id", String(selectedStrainId));
    formData.append("file", selectedFile);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/analysis/upload/${selectedAnalysisType}`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setUploadSuccess(response.data.message || "Archivo subido con éxito.");
      setTaskId(response.data.task_id); // Guardar el ID de la tarea
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
    <div className="ceparium-page">
      <h1>Página Ceparium</h1>

      <section className="data-visualization">
        <h2>Visualización de Organismos</h2>
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
      </section>

      <section className="file-upload">
        <h2>Carga de Archivos</h2>
        <div>
          <label htmlFor="strain-select">Seleccionar Cepa:</label>
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
                  {strain.name} (Organismo: {strain.organism_id})
                </option>
              ))}
            </select>
          )}
        </div>

        <div className="upload-section">
          <label htmlFor="analysis-type-select">Tipo de Análisis:</label>
          <select
            id="analysis-type-select"
            value={selectedAnalysisType}
            onChange={(e) => setSelectedAnalysisType(e.target.value)}
            className="form-control"
          >
            <option value="fasta_count">FASTA Count</option>
            <option value="fasta_gc_content">FASTA GC Content</option>
            <option value="fastq_stats">FASTQ Stats</option>
            <option value="genbank_stats">GenBank Stats</option>
            <option value="gff_stats">GFF Stats</option>
          </select>
        </div>

        <div className="upload-section">
          <input type="file" onChange={handleFileChange} className="form-control" />
          <button
            onClick={handleFileUpload}
            disabled={!selectedFile || !selectedStrainId || uploading}
            className="button-primary"
          >
            {uploading ? "Subiendo..." : "Subir Archivo"}
          </button>
        </div>

        {selectedFile && <p>Archivo seleccionado: {selectedFile.name}</p>}
        {uploading && <p>Cargando archivo...</p>}
        {uploadError && <p className="error-message">{uploadError}</p>}
        {uploadSuccess && <p className="success-message">{uploadSuccess}</p>}

        {taskId && (
          <div className="analysis-status">
            <h3>Estado de la Tarea de Análisis (ID: {taskId})</h3>
            {taskStatus ? (
              <div>
                <p>Estado: {taskStatus.status}</p>
                {taskStatus.progress !== undefined && (
                  <p>Progreso: {taskStatus.progress}%</p>
                )}
                {taskStatus.state === "SUCCESS" && taskStatus.result && (
                  <div className="analysis-results">
                    <h4>Resultados:</h4>
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
        )}
      </section>
    </div>
  );
};

export default CepariumPage;
