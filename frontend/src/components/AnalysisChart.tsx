import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface AnalysisChartProps {
  analysisType: string;
  results: Record<string, any>;
}

const AnalysisChart: React.FC<AnalysisChartProps> = ({ analysisType, results }) => {
  if (!results) {
    return (
      <div className="chart-placeholder">
        No hay datos para graficar
      </div>
    );
  }

  // Chart for FASTA count analysis
  if (analysisType === 'fasta_count' && results.sequence_count !== undefined) {
    const data = {
      labels: ['Secuencias'],
      datasets: [
        {
          label: 'Número de Secuencias',
          data: [results.sequence_count],
          backgroundColor: 'rgba(75, 192, 192, 0.5)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1,
        },
      ],
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top' as const,
        },
        title: {
          display: true,
          text: 'Conteo de Secuencias FASTA',
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        },
      },
    };

    return (
      <div style={{ height: '300px' }}>
        <Bar data={data} options={options} />
      </div>
    );
  }

  // Chart for FASTA GC content analysis
  if (analysisType === 'fasta_gc_content') {
    if (results.individual_gc_contents && Array.isArray(results.individual_gc_contents)) {
      const gcContents = results.individual_gc_contents;
      const labels = Array.from({ length: gcContents.length }, (_, i) => `Seq ${i + 1}`);

      const data = {
        labels,
        datasets: [
          {
            label: 'GC Content (%)',
            data: gcContents,
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
          },
        ],
      };

      const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top' as const,
          },
          title: {
            display: true,
            text: 'GC Content por Secuencia',
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'GC Content (%)',
            },
          },
        },
      };

      return (
        <div style={{ height: '300px' }}>
          <Bar data={data} options={options} />
        </div>
      );
    } else if (results.average_gc_content !== undefined) {
      // Si solo tenemos el promedio
      const data = {
        labels: ['GC Promedio'],
        datasets: [
          {
            label: 'GC Content (%)',
            data: [results.average_gc_content],
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
          },
        ],
      };

      const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top' as const,
          },
          title: {
            display: true,
            text: 'GC Content Promedio',
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'GC Content (%)',
            },
          },
        },
      };

      return (
        <div style={{ height: '300px' }}>
          <Bar data={data} options={options} />
        </div>
      );
    }
  }

  // Chart for GFF feature counts
  if (analysisType === 'gff_stats' && results.feature_counts) {
    const featureCounts = results.feature_counts;
    const labels = Object.keys(featureCounts);
    const dataValues = Object.values(featureCounts).map(v => 
      typeof v === 'number' ? v : parseInt(v) || 0
    );

    const data = {
      labels,
      datasets: [
        {
          label: 'Cantidad',
          data: dataValues,
          backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 205, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)',
            'rgba(255, 159, 64, 0.5)',
          ],
          borderColor: [
            'rgb(255, 99, 132)',
            'rgb(54, 162, 235)',
            'rgb(255, 205, 86)',
            'rgb(75, 192, 192)',
            'rgb(153, 102, 255)',
            'rgb(255, 159, 64)',
          ],
          borderWidth: 1,
        },
      ],
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top' as const,
        },
        title: {
          display: true,
          text: 'Distribución de Features GFF',
        },
      },
    };

    return (
      <div style={{ height: '300px' }}>
        <Pie data={data} options={options} />
      </div>
    );
  }

  // Chart for FASTQ stats analysis
  if (analysisType === 'fastq_stats') {
    const labels = [];
    const dataValues = [];

    if (results.avg_sequence_length !== undefined) {
      labels.push('Longitud Promedio');
      dataValues.push(results.avg_sequence_length);
    }

    if (results.overall_avg_quality !== undefined) {
      labels.push('Calidad Promedio');
      dataValues.push(results.overall_avg_quality);
    }

    if (labels.length > 0) {
      const data = {
        labels,
        datasets: [
          {
            label: 'Valores',
            data: dataValues,
            backgroundColor: [
              'rgba(255, 99, 132, 0.5)',
              'rgba(54, 162, 235, 0.5)',
            ],
            borderColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
            ],
            borderWidth: 1,
          },
        ],
      };

      const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top' as const,
          },
          title: {
            display: true,
            text: 'Estadísticas FASTQ',
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      };

      return (
        <div style={{ height: '300px' }}>
          <Bar data={data} options={options} />
        </div>
      );
    }
  }

  // Chart for GenBank stats analysis
  if (analysisType === 'genbank_stats') {
    const labels = [];
    const dataValues = [];

    if (results.sequence_length !== undefined) {
      labels.push('Longitud Secuencia');
      dataValues.push(results.sequence_length);
    }

    if (results.feature_count !== undefined) {
      labels.push('Cantidad de Features');
      dataValues.push(results.feature_count);
    }

    if (labels.length > 0) {
      const data = {
        labels,
        datasets: [
          {
            label: 'Valores',
            data: dataValues,
            backgroundColor: [
              'rgba(255, 159, 64, 0.5)',
              'rgba(153, 102, 255, 0.5)',
            ],
            borderColor: [
              'rgba(255, 159, 64, 1)',
              'rgba(153, 102, 255, 1)',
            ],
            borderWidth: 1,
          },
        ],
      };

      const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top' as const,
          },
          title: {
            display: true,
            text: 'Estadísticas GenBank',
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      };

      return (
        <div style={{ height: '300px' }}>
          <Bar data={data} options={options} />
        </div>
      );
    }
  }

  return (
    <div className="chart-placeholder">
      Tipo de análisis no soportado o datos incompletos: {analysisType}
    </div>
  );
};

export default AnalysisChart;