import React from 'react';
import FileUploadComponent from '../components/FileUploadComponent';

const GenericMinioUploadPage: React.FC = () => {
  return (
    <div className="bioinformatics-theme">
      <div className="bioinformatics-card">
        <h1>Carga de Archivos Genérica</h1>
        <p>Guarda archivos de microorganismos, como FASTA, FASTQ, GenBank, GFF u otros formatos biológicos.</p>

        <div className="file-upload-section">
          <FileUploadComponent /> {/* Carga genérica sin asociación a cepas */}
        </div>
      </div>
    </div>
  );
};

export default GenericMinioUploadPage;
