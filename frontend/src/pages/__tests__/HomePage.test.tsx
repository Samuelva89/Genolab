import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Mock, vi } from 'vitest';
import axios from 'axios';
import '@testing-library/jest-dom';
import HomePage from '../HomePage';

// Mock de axios
vi.mock('axios');
const mockAxios = axios as Mock;

describe('HomePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch and display summary statistics', async () => {
    const mockOrganisms = [
      { id: 1, name: 'Saccharomyces cerevisiae', genus: 'Saccharomyces', species: 'cerevisiae' }
    ];

    const mockStrains = [
      { id: 1, strain_name: 'Strain A', source: 'Lab', organism_id: 1 }
    ];

    const mockAnalyses = [
      { id: 1, analysis_type: 'fasta_count', results: { count: 10 }, timestamp: '2023-01-01', strain_id: 1, owner_id: 1 }
    ];

    mockAxios.get
      .mockResolvedValueOnce({ data: mockOrganisms }) // Organismos
      .mockResolvedValueOnce({ data: mockStrains });  // Cepas

    // Mock para análisis: se hacen múltiples llamadas para cada cepa
    mockAxios.get.mockResolvedValueOnce({ data: mockAnalyses }); // Análisis para cepa 1

    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>
    );

    // Verificar que se muestre el mensaje de carga inicialmente
    expect(screen.getByText(/Cargando estadísticas del sistema.../i)).toBeInTheDocument();

    // Esperar a que se muestren las estadísticas
    await waitFor(() => {
      expect(screen.getByText(/Organismos/i)).toBeInTheDocument();
      expect(screen.getByText(/Cepas/i)).toBeInTheDocument();
      expect(screen.getByText(/Análisis/i)).toBeInTheDocument();
    });

    // Verificar que se muestren los números correctos
    expect(screen.getByText('1')).toBeInTheDocument(); // Número de organismos
    expect(screen.getByText('1')).toBeInTheDocument(); // Número de cepas
    expect(screen.getByText('1')).toBeInTheDocument(); // Número de análisis

    // Verificar que se hayan llamado las APIs correctas
    expect(mockAxios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/ceparium/organisms/'
    );
    expect(mockAxios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/ceparium/strains/'
    );
    expect(mockAxios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/analysis/strain/1'
    );
  });

  it('should handle statistics loading error gracefully', async () => {
    mockAxios.get.mockRejectedValueOnce(new Error('Network error'));

    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>
    );

    // Esperar a que se carguen las estadísticas (aunque fallen)
    await waitFor(() => {
      // Aunque fallan, se espera que se muestre la página con valores 0
      expect(screen.getByText('0')).toBeInTheDocument(); // Número de organismos
      expect(screen.getByText('0')).toBeInTheDocument(); // Número de cepas
      expect(screen.getByText('0')).toBeInTheDocument(); // Número de análisis
    });
  });

  it('should display welcome message and description', async () => {
    // Mock para estadísticas vacías
    mockAxios.get
      .mockResolvedValueOnce({ data: [] }) // Organismos vacíos
      .mockResolvedValueOnce({ data: [] });  // Cepas vacías

    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Bienvenido a GENOLAB/i)).toBeInTheDocument();
      expect(screen.getByText(/Plataforma de análisis genómico/i)).toBeInTheDocument();
      expect(screen.getByText(/Sistema integral para la gestión de cepas microbianas y análisis bioinformáticos./i)).toBeInTheDocument();
    });
  });

  it('should show quick action cards with correct links', async () => {
    // Mock para estadísticas vacías
    mockAxios.get
      .mockResolvedValueOnce({ data: [] }) // Organismos vacíos
      .mockResolvedValueOnce({ data: [] });  // Cepas vacías

    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Acciones Rápidas/i)).toBeInTheDocument();
    });

    // Verificar que los enlaces de acción rápida estén presentes
    expect(screen.getByRole('link', { name: /Crear Organismo/i })).toHaveAttribute('href', '/ceparium/organisms/create');
    expect(screen.getByRole('link', { name: /Subir Archivo/i })).toHaveAttribute('href', '/ceparium');
    expect(screen.getByRole('link', { name: /Explorar/i })).toHaveAttribute('href', '/ceparium/organisms');
  });

  it('should handle multiple strains with analyses', async () => {
    const mockOrganisms = [
      { id: 1, name: 'Saccharomyces cerevisiae', genus: 'Saccharomyces', species: 'cerevisiae' },
      { id: 2, name: 'Escherichia coli', genus: 'Escherichia', species: 'coli' }
    ];

    const mockStrains = [
      { id: 1, strain_name: 'Strain A', source: 'Lab', organism_id: 1 },
      { id: 2, strain_name: 'Strain B', source: 'Lab', organism_id: 2 }
    ];

    const mockAnalyses = [
      { id: 1, analysis_type: 'fasta_count', results: { count: 10 }, timestamp: '2023-01-01', strain_id: 1, owner_id: 1 }
    ];

    mockAxios.get
      .mockResolvedValueOnce({ data: mockOrganisms }) // Organismos
      .mockResolvedValueOnce({ data: mockStrains });  // Cepas

    // Mock para análisis: múltiples llamadas para cada cepa
    mockAxios.get
      .mockResolvedValueOnce({ data: mockAnalyses })  // Análisis para cepa 1
      .mockResolvedValueOnce({ data: mockAnalyses }); // Análisis para cepa 2

    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument(); // Número de organismos
      expect(screen.getByText('2')).toBeInTheDocument(); // Número de cepas
      expect(screen.getByText('2')).toBeInTheDocument(); // Número total de análisis (1+1)
    });
  });

  it('should handle strain without analyses gracefully', async () => {
    const mockOrganisms = [
      { id: 1, name: 'Saccharomyces cerevisiae', genus: 'Saccharomyces', species: 'cerevisiae' }
    ];

    const mockStrains = [
      { id: 1, strain_name: 'Strain A', source: 'Lab', organism_id: 1 }
    ];

    // Mock para análisis que falla para una cepa (no tiene análisis)
    mockAxios.get
      .mockResolvedValueOnce({ data: mockOrganisms }) // Organismos
      .mockResolvedValueOnce({ data: mockStrains })   // Cepas
      .mockRejectedValueOnce(new Error('No analyses')); // Análisis falla para la cepa

    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument(); // Número de organismos
      expect(screen.getByText('1')).toBeInTheDocument(); // Número de cepas
      expect(screen.getByText('0')).toBeInTheDocument(); // Número de análisis (0 porque falló)
    });
  });
});