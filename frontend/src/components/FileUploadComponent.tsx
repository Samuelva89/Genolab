import React, { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../services/api';

interface FileUploadComponentProps {
  strainId: number;
  onUploadSuccess?: () => void;
  allowedExtensions?: string[];
}

const FileUploadComponent: React.FC<FileUploadComponentProps> = ({
  strainId,
  onUploadSuccess,
  allowedExtensions = ['.fasta', '.fastq', '.gbk', '.gff', '.txt', '.fa', '.fas', '.mfasta', '.fna', '.faa']
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [uploadMessage, setUploadMessage] = useState<string>('');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];

      // Validate file extension
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!allowedExtensions.includes(fileExtension)) {
        setUploadMessage(`Extensión de archivo no permitida. Extensiones permitidas: ${allowedExtensions.join(', ')}`);
        setUploadStatus('error');
        return;
      }

      setSelectedFile(file);
      setUploadStatus('idle');
      setUploadMessage('');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadMessage('Por favor seleccione un archivo primero');
      setUploadStatus('error');
      return;
    }

    setUploadStatus('uploading');
    setUploadMessage('Subiendo archivo...');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('strain_id', strainId.toString());
      formData.append('analysis_type', 'raw_file');

      const response = await axios.post(`${API_BASE_URL}/api/analysis/upload/raw`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadStatus('success');
      setUploadMessage(`Archivo subido exitosamente a MinIO. ID de análisis: ${response.data.analysis_id || 'N/A'}`);

      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadStatus('error');
      // Manejo de error más específico
      if (axios.isAxiosError(error)) {
        setUploadMessage(`Error al subir el archivo: ${error.response?.data?.detail || error.message}`);
      } else {
        setUploadMessage('Error al subir el archivo: ' + (error as Error).message);
      }
    }
  };

  return (
    <div className="bioinformatics-card file-upload-component">
      <h3>Subir archivo individual</h3>
      <p>Sube archivos FASTA, FASTQ, GenBank, GFF u otros formatos biológicos directamente a MinIO</p>

      <div className="file-upload-area bioinformatics-form">
        <input
          type="file"
          onChange={handleFileChange}
          accept={allowedExtensions.join(',')}
          disabled={uploadStatus === 'uploading'}
          className="file-input"
        />

        {selectedFile && (
          <div className="file-info">
            <p>Archivo seleccionado: {selectedFile.name}</p>
            <p>Tamaño: ${(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!selectedFile || uploadStatus === 'uploading'}
          className={`upload-btn ${uploadStatus} bioinformatics-button`}
        >
          {uploadStatus === 'uploading' ? 'Subiendo...' : 'Subir archivo a MinIO'}
        </button>

        {uploadStatus !== 'idle' && (
          <div className={`status-message ${uploadStatus} bioinformatics-message`}>
            {uploadMessage}
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUploadComponent;