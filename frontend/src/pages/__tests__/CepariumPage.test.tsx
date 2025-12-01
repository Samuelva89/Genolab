import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Mock, vi } from 'vitest';
import axios from 'axios';
import '@testing-library/jest-dom';
import CepariumPage from '../CepariumPage';

// Mock de axios
vi.mock('axios');
const mockAxios = axios as Mock;

describe('CepariumPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch and display organisms and strains', async () => {
    const mockOrganisms = [
      {
        id: 1,
        name: 'Saccharomyces cerevisiae',
        genus: 'Saccharomyces',
        species: 'cerevisiae'
      }
    ];

    const mockStrains = [
      {
        id: 1,
        strain_name: 'Strain A',
        source: 'Lab collection',
        organism_id: 1
      }
    ];

    mockAxios.get
      .mockResolvedValueOnce({ data: mockOrganisms })  // Para obtener organismos
      .mockResolvedValueOnce({ data: mockStrains });   // Para obtener cepas

    render(
      <MemoryRouter>
        <CepariumPage />
      </MemoryRouter>
    );

    // Verificar que se muestren los organismos cargados
    await waitFor(() => {
      expect(screen.getByText(/Saccharomyces cerevisiae \(Saccharomyces cerevisiae\)/i)).toBeInTheDocument();
    });

    // Verificar que se hayan llamado las APIs correctas
    expect(mockAxios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/ceparium/organisms/'
    );
    expect(mockAxios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/ceparium/strains/'
    );
  });

  it('should handle file upload successfully', async () => {
    const mockOrganisms = [{ id: 1, name: 'Saccharomyces cerevisiae', genus: 'Saccharomyces', species: 'cerevisiae' }];
    const mockStrains = [{ id: 1, strain_name: 'Strain A', source: 'Lab', organism_id: 1 }];
    const mockUploadResponse = { message: 'Archivo subido con éxito.', task_id: 'task-123' };

    mockAxios.get
      .mockResolvedValueOnce({ data: mockOrganisms })
      .mockResolvedValueOnce({ data: mockStrains });
    mockAxios.post.mockResolvedValueOnce({ data: mockUploadResponse });

    render(
      <MemoryRouter>
        <CepariumPage />
      </MemoryRouter>
    );

    // Esperar a que se carguen los datos
    await waitFor(() => {
      expect(screen.getByText(/Saccharomyces cerevisiae \(Saccharomyces cerevisiae\)/i)).toBeInTheDocument();
    });

    // Seleccionar una cepa
    const strainSelect = screen.getByRole('combobox', { name: /Seleccionar Cepa:/i });
    fireEvent.change(strainSelect, { target: { value: '1' } });

    // Seleccionar tipo de análisis
    const analysisSelect = screen.getByRole('combobox', { name: /Tipo de Análisis:/i });
    fireEvent.change(analysisSelect, { target: { value: 'fasta_count' } });

    // Simular la selección de un archivo
    const fileInput = screen.getByLabelText(/Seleccionar Archivo:/i);
    const file = new File(['dummy file content'], 'test.fasta', { type: 'text/plain' });
    fireEvent.change(fileInput, { target: { files: [file] } });

    // Esperar a que se actualice el estado del archivo
    await waitFor(() => {
      expect(screen.getByText(/Archivo seleccionado: test.fasta/i)).toBeInTheDocument();
    });

    // Hacer click en el botón de subir
    fireEvent.click(screen.getByRole('button', { name: /Subir Archivo/i }));

    // Verificar que se haya llamado a la API de subida
    await waitFor(() => {
      expect(mockAxios.post).toHaveBeenCalledWith(
        'http://localhost:8000/api/analysis/upload/fasta_count',
        expect.any(FormData),
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
    });

    // Verificar que se muestre el mensaje de éxito
    expect(screen.getByText(/Archivo subido con éxito./i)).toBeInTheDocument();
  });

  it('should show error when no file is selected', async () => {
    const mockOrganisms = [{ id: 1, name: 'Saccharomyces cerevisiae', genus: 'Saccharomyces', species: 'cerevisiae' }];
    const mockStrains = [{ id: 1, strain_name: 'Strain A', source: 'Lab', organism_id: 1 }];

    mockAxios.get
      .mockResolvedValueOnce({ data: mockOrganisms })
      .mockResolvedValueOnce({ data: mockStrains });

    render(
      <MemoryRouter>
        <CepariumPage />
      </MemoryRouter>
    );

    // Esperar a que se carguen los datos
    await waitFor(() => {
      expect(screen.getByText(/Saccharomyces cerevisiae \(Saccharomyces cerevisiae\)/i)).toBeInTheDocument();
    });

    // Seleccionar una cepa
    const strainSelect = screen.getByRole('combobox', { name: /Seleccionar Cepa:/i });
    fireEvent.change(strainSelect, { target: { value: '1' } });

    // Hacer click en el botón de subir sin seleccionar archivo
    fireEvent.click(screen.getByRole('button', { name: /Subir Archivo/i }));

    // Verificar que se muestre el mensaje de error
    await waitFor(() => {
      expect(screen.getByText(/Por favor, selecciona un archivo para subir./i)).toBeInTheDocument();
    });
  });

  it('should show error when no strain is selected', async () => {
    const mockOrganisms = [{ id: 1, name: 'Saccharomyces cerevisiae', genus: 'Saccharomyces', species: 'cerevisiae' }];
    const mockStrains = [{ id: 1, strain_name: 'Strain A', source: 'Lab', organism_id: 1 }];

    mockAxios.get
      .mockResolvedValueOnce({ data: mockOrganisms })
      .mockResolvedValueOnce({ data: mockStrains });

    render(
      <MemoryRouter>
        <CepariumPage />
      </MemoryRouter>
    );

    // Esperar a que se carguen los datos
    await waitFor(() => {
      expect(screen.getByText(/Saccharomyces cerevisiae \(Saccharomyces cerevisiae\)/i)).toBeInTheDocument();
    });

    // Simular la selección de un archivo sin seleccionar cepa
    const fileInput = screen.getByLabelText(/Seleccionar Archivo:/i);
    const file = new File(['dummy file content'], 'test.fasta', { type: 'text/plain' });
    fireEvent.change(fileInput, { target: { files: [file] } });

    // Esperar a que se actualice el estado del archivo
    await waitFor(() => {
      expect(screen.getByText(/Archivo seleccionado: test.fasta/i)).toBeInTheDocument();
    });

    // Hacer click en el botón de subir sin seleccionar cepa
    fireEvent.click(screen.getByRole('button', { name: /Subir Archivo/i }));

    // Verificar que se muestre el mensaje de error
    await waitFor(() => {
      expect(screen.getByText(/Por favor, selecciona una cepa./i)).toBeInTheDocument();
    });
  });

  it('should handle upload error', async () => {
    const mockOrganisms = [{ id: 1, name: 'Saccharomyces cerevisiae', genus: 'Saccharomyces', species: 'cerevisiae' }];
    const mockStrains = [{ id: 1, strain_name: 'Strain A', source: 'Lab', organism_id: 1 }];

    mockAxios.get
      .mockResolvedValueOnce({ data: mockOrganisms })
      .mockResolvedValueOnce({ data: mockStrains });
    mockAxios.post.mockRejectedValueOnce({
      response: { data: { detail: 'Error al subir el archivo' } }
    });

    render(
      <MemoryRouter>
        <CepariumPage />
      </MemoryRouter>
    );

    // Esperar a que se carguen los datos
    await waitFor(() => {
      expect(screen.getByText(/Saccharomyces cerevisiae \(Saccharomyces cerevisiae\)/i)).toBeInTheDocument();
    });

    // Seleccionar una cepa
    const strainSelect = screen.getByRole('combobox', { name: /Seleccionar Cepa:/i });
    fireEvent.change(strainSelect, { target: { value: '1' } });

    // Simular la selección de un archivo
    const fileInput = screen.getByLabelText(/Seleccionar Archivo:/i);
    const file = new File(['dummy file content'], 'test.fasta', { type: 'text/plain' });
    fireEvent.change(fileInput, { target: { files: [file] } });

    // Esperar a que se actualice el estado del archivo
    await waitFor(() => {
      expect(screen.getByText(/Archivo seleccionado: test.fasta/i)).toBeInTheDocument();
    });

    // Hacer click en el botón de subir
    fireEvent.click(screen.getByRole('button', { name: /Subir Archivo/i }));

    // Verificar que se muestre el mensaje de error de la API
    await waitFor(() => {
      expect(screen.getByText(/Error al subir el archivo./i)).toBeInTheDocument();
    });
  });

  it('should show loading state when uploading', async () => {
    const mockOrganisms = [{ id: 1, name: 'Saccharomyces cerevisiae', genus: 'Saccharomyces', species: 'cerevisiae' }];
    const mockStrains = [{ id: 1, strain_name: 'Strain A', source: 'Lab', organism_id: 1 }];

    mockAxios.get
      .mockResolvedValueOnce({ data: mockOrganisms })
      .mockResolvedValueOnce({ data: mockStrains });

    render(
      <MemoryRouter>
        <CepariumPage />
      </MemoryRouter>
    );

    // Esperar a que se carguen los datos
    await waitFor(() => {
      expect(screen.getByText(/Saccharomyces cerevisiae \(Saccharomyces cerevisiae\)/i)).toBeInTheDocument();
    });

    // Seleccionar una cepa
    const strainSelect = screen.getByRole('combobox', { name: /Seleccionar Cepa:/i });
    fireEvent.change(strainSelect, { target: { value: '1' } });

    // Simular la selección de un archivo
    const fileInput = screen.getByLabelText(/Seleccionar Archivo:/i);
    const file = new File(['dummy file content'], 'test.fasta', { type: 'text/plain' });
    fireEvent.change(fileInput, { target: { files: [file] } });

    // Esperar a que se actualice el estado del archivo
    await waitFor(() => {
      expect(screen.getByText(/Archivo seleccionado: test.fasta/i)).toBeInTheDocument();
    });

    // Mock para que la promesa se resuelva después de un tiempo
    const mockPostPromise = new Promise((resolve) => {
      setTimeout(() => resolve({ data: { message: 'Archivo subido.', task_id: 'task-123' } }), 100);
    });
    mockAxios.post.mockReturnValue(mockPostPromise);

    // Hacer click en el botón de subir
    fireEvent.click(screen.getByRole('button', { name: /Subir Archivo/i }));

    // Verificar que el botón esté deshabilitado (cargando)
    const uploadButton = screen.getByRole('button', { name: /Subiendo.../i });
    expect(uploadButton).toBeDisabled();
  });

  it('should handle organism loading error', async () => {
    mockAxios.get.mockRejectedValueOnce(new Error('Network error'));

    render(
      <MemoryRouter>
        <CepariumPage />
      </MemoryRouter>
    );

    // Esperar a que se muestre el mensaje de error
    await waitFor(() => {
      expect(screen.getByText(/Error al cargar los organismos./i)).toBeInTheDocument();
    });
  });

  it('should handle strain loading error', async () => {
    const mockOrganisms = [{ id: 1, name: 'Saccharomyces cerevisiae', genus: 'Saccharomyces', species: 'cerevisiae' }];

    mockAxios.get
      .mockResolvedValueOnce({ data: mockOrganisms })
      .mockRejectedValueOnce(new Error('Network error'));

    render(
      <MemoryRouter>
        <CepariumPage />
      </MemoryRouter>
    );

    // Esperar a que se muestre el mensaje de error de cepas
    await waitFor(() => {
      expect(screen.getByText(/Error al cargar las cepas./i)).toBeInTheDocument();
    });
  });
});