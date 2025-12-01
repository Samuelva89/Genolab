import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Mock, vi } from 'vitest';
import axios from 'axios';
import '@testing-library/jest-dom';
import OrganismListPage from '../OrganismListPage';

// Mock de axios
vi.mock('axios');
const mockAxios = axios as Mock;

describe('OrganismListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch and display list of organisms', async () => {
    const mockOrganisms = [
      {
        id: 1,
        name: 'Saccharomyces cerevisiae',
        genus: 'Saccharomyces',
        species: 'cerevisiae'
      },
      {
        id: 2,
        name: 'Escherichia coli',
        genus: 'Escherichia',
        species: 'coli'
      }
    ];

    mockAxios.get.mockResolvedValueOnce({ data: mockOrganisms });

    render(
      <MemoryRouter>
        <OrganismListPage />
      </MemoryRouter>
    );

    // Verificar que se muestre el mensaje de carga inicialmente
    expect(screen.getByText(/Cargando organismos.../i)).toBeInTheDocument();

    // Esperar a que se carguen los organismos
    await waitFor(() => {
      expect(screen.getByText('Saccharomyces cerevisiae (Saccharomyces cerevisiae)')).toBeInTheDocument();
      expect(screen.getByText('Escherichia coli (Escherichia coli)')).toBeInTheDocument();
    });

    // Verificar que se haya llamado a la API correcta
    expect(mockAxios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/ceparium/organisms/'
    );
  });

  it('should show error message when fetching organisms fails', async () => {
    mockAxios.get.mockRejectedValueOnce(new Error('Network error'));

    render(
      <MemoryRouter>
        <OrganismListPage />
      </MemoryRouter>
    );

    // Esperar a que se muestre el mensaje de error
    await waitFor(() => {
      expect(screen.getByText(/Error al cargar los organismos./i)).toBeInTheDocument();
    });
  });

  it('should show message when no organisms are found', async () => {
    mockAxios.get.mockResolvedValueOnce({ data: [] });

    render(
      <MemoryRouter>
        <OrganismListPage />
      </MemoryRouter>
    );

    // Esperar a que se muestre el mensaje de no hay organismos
    await waitFor(() => {
      expect(screen.getByText(/No hay organismos registrados./i)).toBeInTheDocument();
    });
  });

  it('should handle delete organism function', async () => {
    const mockOrganisms = [
      {
        id: 1,
        name: 'Saccharomyces cerevisiae',
        genus: 'Saccharomyces',
        species: 'cerevisiae'
      }
    ];

    mockAxios.get.mockResolvedValueOnce({ data: mockOrganisms });
    mockAxios.delete.mockResolvedValueOnce({});

    // Mock de window.confirm para devolver true
    const originalConfirm = window.confirm;
    window.confirm = vi.fn(() => true);

    render(
      <MemoryRouter>
        <OrganismListPage />
      </MemoryRouter>
    );

    // Esperar a que se carguen los organismos
    await waitFor(() => {
      expect(screen.getByText('Saccharomyces cerevisiae (Saccharomyces cerevisiae)')).toBeInTheDocument();
    });

    // Simular click en el botón de eliminar
    const deleteButton = screen.getByRole('button', { name: /Eliminar/i });
    deleteButton.click();

    // Verificar que se haya llamado a la API de eliminación
    await waitFor(() => {
      expect(mockAxios.delete).toHaveBeenCalledWith(
        'http://localhost:8000/api/ceparium/organisms/1'
      );
    });

    // Restaurar confirm original
    window.confirm = originalConfirm;
  });

  it('should handle delete organism cancellation', async () => {
    const mockOrganisms = [
      {
        id: 1,
        name: 'Saccharomyces cerevisiae',
        genus: 'Saccharomyces',
        species: 'cerevisiae'
      }
    ];

    mockAxios.get.mockResolvedValueOnce({ data: mockOrganisms });

    // Mock de window.confirm para devolver false (cancelar)
    const originalConfirm = window.confirm;
    window.confirm = vi.fn(() => false);

    render(
      <MemoryRouter>
        <OrganismListPage />
      </MemoryRouter>
    );

    // Esperar a que se carguen los organismos
    await waitFor(() => {
      expect(screen.getByText('Saccharomyces cerevisiae (Saccharomyces cerevisiae)')).toBeInTheDocument();
    });

    // Simular click en el botón de eliminar
    const deleteButton = screen.getByRole('button', { name: /Eliminar/i });
    deleteButton.click();

    // Verificar que NO se haya llamado a la API de eliminación
    expect(mockAxios.delete).not.toHaveBeenCalled();

    // Restaurar confirm original
    window.confirm = originalConfirm;
  });

  it('should handle delete organism error', async () => {
    const mockOrganisms = [
      {
        id: 1,
        name: 'Saccharomyces cerevisiae',
        genus: 'Saccharomyces',
        species: 'cerevisiae'
      }
    ];

    mockAxios.get.mockResolvedValueOnce({ data: mockOrganisms });
    mockAxios.delete.mockRejectedValueOnce(new Error('Delete error'));

    // Mock de window.confirm para devolver true
    const originalConfirm = window.confirm;
    window.confirm = vi.fn(() => true);

    render(
      <MemoryRouter>
        <OrganismListPage />
      </MemoryRouter>
    );

    // Esperar a que se carguen los organismos
    await waitFor(() => {
      expect(screen.getByText('Saccharomyces cerevisiae (Saccharomyces cerevisiae)')).toBeInTheDocument();
    });

    // Simular click en el botón de eliminar
    const deleteButton = screen.getByRole('button', { name: /Eliminar/i });
    deleteButton.click();

    // Esperar a que se muestre el mensaje de error
    await waitFor(() => {
      expect(screen.getByText(/Error al eliminar el organismo./i)).toBeInTheDocument();
    });

    // Restaurar confirm original
    window.confirm = originalConfirm;
  });
});