import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Mock, vi } from 'vitest';
import axios from 'axios';
import '@testing-library/jest-dom';
import OrganismFormPage from '../OrganismFormPage';

// Mock de axios
vi.mock('axios');
const mockAxios = axios as Mock;

describe('OrganismFormPage', () => {
  const mockNavigate = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom');
      return {
        ...actual,
        useNavigate: () => mockNavigate,
        useParams: () => ({ id: undefined }),
      };
    });
  });

  it('should render the create organism form correctly', () => {
    render(
      <MemoryRouter>
        <OrganismFormPage />
      </MemoryRouter>
    );

    expect(screen.getByText(/Crear Nuevo Organismo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Nombre:/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Género:/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Especie:/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Crear Organismo/i })).toBeInTheDocument();
  });

  it('should submit a new organism successfully', async () => {
    const newOrganism = {
      id: 1,
      name: 'Saccharomyces cerevisiae',
      genus: 'Saccharomyces',
      species: 'cerevisiae'
    };

    // Mock para la creación de un organismo
    mockAxios.post.mockResolvedValueOnce({ data: newOrganism });

    render(
      <MemoryRouter>
        <OrganismFormPage />
      </MemoryRouter>
    );

    // Rellenar el formulario
    fireEvent.change(screen.getByLabelText(/Nombre:/i), {
      target: { value: 'Saccharomyces cerevisiae' }
    });
    fireEvent.change(screen.getByLabelText(/Género:/i), {
      target: { value: 'Saccharomyces' }
    });
    fireEvent.change(screen.getByLabelText(/Especie:/i), {
      target: { value: 'cerevisiae' }
    });

    // Hacer click en el botón de submit
    fireEvent.click(screen.getByRole('button', { name: /Crear Organismo/i }));

    // Verificar que se haya llamado a la API correcta
    await waitFor(() => {
      expect(mockAxios.post).toHaveBeenCalledWith(
        'http://localhost:8000/api/ceparium/organisms/',
        {
          name: 'Saccharomyces cerevisiae',
          genus: 'Saccharomyces',
          species: 'cerevisiae'
        }
      );
    });

    // Verificar que se muestre el mensaje de éxito
    expect(screen.getByText(/Organismo creado exitosamente./i)).toBeInTheDocument();
  });

  it('should show error message when submission fails', async () => {
    // Mock para fallar la creación de un organismo
    mockAxios.post.mockRejectedValueOnce({
      response: { data: { detail: 'Error al crear el organismo' } }
    });

    render(
      <MemoryRouter>
        <OrganismFormPage />
      </MemoryRouter>
    );

    // Rellenar el formulario
    fireEvent.change(screen.getByLabelText(/Nombre:/i), {
      target: { value: 'Saccharomyces cerevisiae' }
    });
    fireEvent.change(screen.getByLabelText(/Género:/i), {
      target: { value: 'Saccharomyces' }
    });
    fireEvent.change(screen.getByLabelText(/Especie:/i), {
      target: { value: 'cerevisiae' }
    });

    // Hacer click en el botón de submit
    fireEvent.click(screen.getByRole('button', { name: /Crear Organismo/i }));

    // Verificar que se muestre el mensaje de error
    await waitFor(() => {
      expect(screen.getByText(/Error al guardar el organismo./i)).toBeInTheDocument();
    });
  });

  it('should render the edit organism form correctly when editing', async () => {
    const existingOrganism = {
      id: 1,
      name: 'Saccharomyces cerevisiae',
      genus: 'Saccharomyces',
      species: 'cerevisiae'
    };

    // Mock para obtener un organismo existente
    mockAxios.get.mockResolvedValueOnce({ data: existingOrganism });
    vi.mock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom');
      return {
        ...actual,
        useNavigate: () => mockNavigate,
        useParams: () => ({ id: '1' }),
      };
    });

    render(
      <MemoryRouter>
        <OrganismFormPage />
      </MemoryRouter>
    );

    // Verificar que se muestre el título de edición
    await waitFor(() => {
      expect(screen.getByText(/Editar Organismo/i)).toBeInTheDocument();
    });

    // Verificar que se llenen los campos con los datos existentes
    expect(screen.getByDisplayValue('Saccharomyces cerevisiae')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Saccharomyces')).toBeInTheDocument();
    expect(screen.getByDisplayValue('cerevisiae')).toBeInTheDocument();

    // Verificar que el botón sea de actualización en lugar de creación
    expect(screen.getByRole('button', { name: /Actualizar Organismo/i })).toBeInTheDocument();
  });

  it('should update an existing organism successfully', async () => {
    const existingOrganism = {
      id: 1,
      name: 'Saccharomyces cerevisiae',
      genus: 'Saccharomyces',
      species: 'cerevisiae'
    };

    const updatedOrganism = {
      id: 1,
      name: 'Saccharomyces pastorianus',
      genus: 'Saccharomyces',
      species: 'pastorianus'
    };

    // Mock para obtener y actualizar un organismo
    mockAxios.get.mockResolvedValueOnce({ data: existingOrganism });
    mockAxios.put.mockResolvedValueOnce({ data: updatedOrganism });

    vi.mock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom');
      return {
        ...actual,
        useNavigate: () => mockNavigate,
        useParams: () => ({ id: '1' }),
      };
    });

    render(
      <MemoryRouter>
        <OrganismFormPage />
      </MemoryRouter>
    );

    // Esperar a que se carguen los datos
    await waitFor(() => {
      expect(screen.getByDisplayValue('Saccharomyces cerevisiae')).toBeInTheDocument();
    });

    // Cambiar los valores
    fireEvent.change(screen.getByLabelText(/Nombre:/i), {
      target: { value: 'Saccharomyces pastorianus' }
    });
    fireEvent.change(screen.getByLabelText(/Especie:/i), {
      target: { value: 'pastorianus' }
    });

    // Hacer click en el botón de actualizar
    fireEvent.click(screen.getByRole('button', { name: /Actualizar Organismo/i }));

    // Verificar que se haya llamado a la API correcta
    await waitFor(() => {
      expect(mockAxios.put).toHaveBeenCalledWith(
        'http://localhost:8000/api/ceparium/organisms/1',
        {
          name: 'Saccharomyces pastorianus',
          genus: 'Saccharomyces',
          species: 'pastorianus'
        }
      );
    });

    // Verificar que se muestre el mensaje de éxito
    expect(screen.getByText(/Organismo actualizado exitosamente./i)).toBeInTheDocument();
  });

  it('should handle loading state correctly', () => {
    // Mock para simular la carga
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    mockAxios.get.mockImplementation(() => new Promise(() => {})); // Promise que no se resuelve

    vi.mock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom');
      return {
        ...actual,
        useNavigate: () => mockNavigate,
        useParams: () => ({ id: '1' }),
      };
    });

    render(
      <MemoryRouter>
        <OrganismFormPage />
      </MemoryRouter>
    );

    // Verificar que se muestre el mensaje de carga
    expect(screen.getByText(/Cargando formulario.../i)).toBeInTheDocument();
  });

  it('should validate required fields', async () => {
    render(
      <MemoryRouter>
        <OrganismFormPage />
      </MemoryRouter>
    );

    // Hacer click en el botón de submit sin rellenar campos
    fireEvent.click(screen.getByRole('button', { name: /Crear Organismo/i }));

    // No se debería llamar a la API
    expect(mockAxios.post).not.toHaveBeenCalled();
  });
});