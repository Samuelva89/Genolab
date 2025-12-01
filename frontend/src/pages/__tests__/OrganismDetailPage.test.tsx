import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Mock, vi } from 'vitest';
import axios from 'axios';
import '@testing-library/jest-dom';
import OrganismDetailPage from '../OrganismDetailPage';

// Mock de axios
vi.mock('axios');
const mockAxios = axios as Mock;

describe('OrganismDetailPage', () => {
  const mockNavigate = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom');
      return {
        ...actual,
        useNavigate: () => mockNavigate,
        useParams: () => ({ id: '1' }),
      };
    });
  });

  it('should fetch and display organism details and strains', async () => {
    const mockOrganism = {
      id: 1,
      name: 'Saccharomyces cerevisiae',
      genus: 'Saccharomyces',
      species: 'cerevisiae'
    };

    const mockStrains = [
      {
        id: 1,
        strain_name: 'Strain A',
        source: 'Lab collection',
        organism_id: 1
      }
    ];

    mockAxios.get
      .mockResolvedValueOnce({ data: mockOrganism })  // Para obtener el organismo
      .mockResolvedValueOnce({ data: mockStrains }); // Para obtener las cepas

    render(
      <MemoryRouter>
        <OrganismDetailPage />
      </MemoryRouter>
    );

    // Verificar que se muestre el mensaje de carga inicialmente
    expect(screen.getByText(/Cargando detalles del organismo.../i)).toBeInTheDocument();

    // Esperar a que se carguen los detalles del organismo
    await waitFor(() => {
      expect(screen.getByText(/Detalles del Organismo: Saccharomyces cerevisiae/i)).toBeInTheDocument();
    });

    // Verificar que se muestren los detalles del organismo
    expect(screen.getByText(/Nombre: Saccharomyces cerevisiae/i)).toBeInTheDocument();
    expect(screen.getByText(/Género: Saccharomyces/i)).toBeInTheDocument();
    expect(screen.getByText(/Especie: cerevisiae/i)).toBeInTheDocument();

    // Verificar que se hayan llamado las APIs correctas
    expect(mockAxios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/ceparium/organisms/1'
    );
    expect(mockAxios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/ceparium/organisms/1/strains'
    );
  });

  it('should show error when organism is not found', async () => {
    mockAxios.get.mockRejectedValueOnce({
      response: { status: 404 }
    });

    render(
      <MemoryRouter>
        <OrganismDetailPage />
      </MemoryRouter>
    );

    // Esperar a que se muestre el mensaje de error
    await waitFor(() => {
      expect(screen.getByText(/Organismo no encontrado./i)).toBeInTheDocument();
    });
  });

  it('should show error when there is a network error', async () => {
    mockAxios.get.mockRejectedValueOnce(new Error('Network error'));

    render(
      <MemoryRouter>
        <OrganismDetailPage />
      </MemoryRouter>
    );

    // Esperar a que se muestre el mensaje de error general
    await waitFor(() => {
      expect(screen.getByText(/Error al cargar los detalles del organismo y sus cepas./i)).toBeInTheDocument();
    });
  });

  it('should handle delete organism function', async () => {
    const mockOrganism = {
      id: 1,
      name: 'Saccharomyces cerevisiae',
      genus: 'Saccharomyces',
      species: 'cerevisiae'
    };

    const mockStrains = [];

    mockAxios.get
      .mockResolvedValueOnce({ data: mockOrganism })
      .mockResolvedValueOnce({ data: mockStrains });
    mockAxios.delete.mockResolvedValueOnce({});

    // Mock de window.confirm para devolver true
    const originalConfirm = window.confirm;
    window.confirm = vi.fn(() => true);

    render(
      <MemoryRouter initialEntries={['/ceparium/organisms/1']}>
        <OrganismDetailPage />
      </MemoryRouter>
    );

    // Esperar a que se carguen los detalles del organismo
    await waitFor(() => {
      expect(screen.getByText(/Detalles del Organismo: Saccharomyces cerevisiae/i)).toBeInTheDocument();
    });

    // Simular click en el botón de eliminar
    const deleteButton = screen.getByRole('button', { name: /Eliminar Organismo/i });
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

  it('should show message when no strains are associated', async () => {
    const mockOrganism = {
      id: 1,
      name: 'Saccharomyces cerevisiae',
      genus: 'Saccharomyces',
      species: 'cerevisiae'
    };

    mockAxios.get
      .mockResolvedValueOnce({ data: mockOrganism })
      .mockResolvedValueOnce({ data: [] }); // Sin cepas

    render(
      <MemoryRouter>
        <OrganismDetailPage />
      </MemoryRouter>
    );

    // Esperar a que se carguen los detalles del organismo
    await waitFor(() => {
      expect(screen.getByText(/Detalles del Organismo: Saccharomyces cerevisiae/i)).toBeInTheDocument();
    });

    // Verificar que se muestre el mensaje de no hay cepas
    expect(screen.getByText(/No hay cepas asociadas a este organismo./i)).toBeInTheDocument();
  });

  it('should handle invalid organism ID', async () => {
    vi.mock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom');
      return {
        ...actual,
        useNavigate: () => mockNavigate,
        useParams: () => ({ id: 'invalid' }),
      };
    });

    render(
      <MemoryRouter>
        <OrganismDetailPage />
      </MemoryRouter>
    );

    // Esperar a que se muestre el mensaje de ID inválido
    await waitFor(() => {
      expect(screen.getByText(/ID de organismo no válido./i)).toBeInTheDocument();
    });
  });
});