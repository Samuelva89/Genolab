import React from 'react';

interface AnalysisResultDisplayProps {
  results: Record<string, any>;
  analysis_type?: string;
}

const AnalysisResultDisplay: React.FC<AnalysisResultDisplayProps> = ({ results, analysis_type }) => {
  // Si es un archivo raw, mostrar información específica
  if (analysis_type === 'raw_file') {
    return (
      <div className="analysis-results-display">
        <div className="raw-file-info">
          <div className="result-item">
            <div className="result-label"><strong>Tipo de archivo:</strong></div>
            <div className="result-value">{results.filename ? (
              <span className="result-string">{results.filename}</span>
            ) : (
              <span className="result-null">n/a</span>
            )}</div>
          </div>

          <div className="result-item">
            <div className="result-label"><strong>Tamaño:</strong></div>
            <div className="result-value">{results.file_size ? (
              <span className="result-number">{results.file_size} bytes</span>
            ) : (
              <span className="result-null">n/a</span>
            )}</div>
          </div>

          <div className="result-item">
            <div className="result-label"><strong>Estado:</strong></div>
            <div className="result-value">{results.upload_status ? (
              <span className={`result-boolean ${results.upload_status === 'completed' ? 'result-boolean-true' : 'result-boolean-false'}`}>
                {results.upload_status === 'completed' ? 'Completado' : results.upload_status}
              </span>
            ) : (
              <span className="result-null">n/a</span>
            )}</div>
          </div>

          <div className="result-item">
            <div className="result-label"><strong>Descripción:</strong></div>
            <div className="result-value">{results.message ? (
              <span className="result-string">{results.message}</span>
            ) : (
              <span className="result-null">n/a</span>
            )}</div>
          </div>
        </div>
      </div>
    );
  }

  // Función para mostrar valores de forma más legible
  const formatValue = (key: string, value: any): React.ReactNode => {
    if (value === null || value === undefined) {
      return <span className="result-null">n/a</span>;
    }

    if (typeof value === 'object') {
      if (Array.isArray(value)) {
        if (value.length === 0) {
          return <span className="result-empty">vacío</span>;
        }
        // Para arrays de números (como GC content), mostramos resumen
        if (value.every(item => typeof item === 'number')) {
          const avg = value.reduce((sum, num) => sum + num, 0) / value.length;
          return (
            <div className="result-array">
              <div><strong>Total:</strong> {value.length} elementos</div>
              <div><strong>Promedio:</strong> {typeof avg === 'number' ? avg.toFixed(2) : avg}</div>
              {value.length <= 5 && <div><strong>Valores:</strong> {value.join(', ')}</div>}
              {value.length > 5 && <details><summary>Ver todos los valores...</summary>{value.join(', ')}</details>}
            </div>
          );
        }
        // Para otros arrays, mostramos cantidad
        return <span className="result-array">{value.length} elementos</span>;
      } else {
        // Para objetos, los mostramos como JSON pero colapsables
        return (
          <details className="result-object-details">
            <summary>{key === 'results' ? 'Detalles' : key}</summary>
            <pre className="result-object-pre">{JSON.stringify(value, null, 2)}</pre>
          </details>
        );
      }
    }

    if (typeof value === 'boolean') {
      return <span className={`result-boolean ${value ? 'result-boolean-true' : 'result-boolean-false'}`}>
        {value ? 'Sí' : 'No'}
      </span>;
    }

    if (typeof value === 'number') {
      // Si es un porcentaje o valor decimal, lo formateamos
      if (key.toLowerCase().includes('percent') || key.toLowerCase().includes('gc_content')) {
        return <span className="result-number">{value.toFixed(2)}%</span>;
      }
      // Si es una longitud o conteo, lo mostramos como número
      if (key.toLowerCase().includes('length') || key.toLowerCase().includes('count')) {
        return <span className="result-number">{value.toLocaleString()}</span>;
      }
      return <span className="result-number">{value}</span>;
    }

    if (typeof value === 'string') {
      // Si es una URL, la formateamos como enlace
      if (value.startsWith('http')) {
        return <a href={value} target="_blank" rel="noopener noreferrer" className="result-link">{value}</a>;
      }
      return <span className="result-string">"{value}"</span>;
    }

    return <span className="result-default">{String(value)}</span>;
  };

  return (
    <div className="analysis-results-display">
      <div className="results-grid">
        {Object.entries(results).map(([key, value]) => (
          <div key={key} className="result-item">
            <div className="result-label">
              <strong>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong>
            </div>
            <div className="result-value">
              {formatValue(key, value)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AnalysisResultDisplay;