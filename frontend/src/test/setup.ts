import '@testing-library/jest-dom';
import { vi } from 'vitest';
import ResizeObserver from 'resize-observer-polyfill';

// Configurar el entorno de pruebas
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: () => false,
  }),
});

// Simular el entorno de navegador
global.ResizeObserver = ResizeObserver;
