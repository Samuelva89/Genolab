import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const handleNavLinkClick = () => {
    // Solo cerrar si el sidebar está abierto (para evitar llamadas innecesarias)
    if (isOpen) {
      onClose();
    }
  };

  return (
    <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
      <div className="sidebar-header">
        <h2>FUNJILAP</h2>
        <button className="sidebar-close-button" onClick={onClose}>
          &times;
        </button>
      </div>
      <nav className="sidebar-nav">
        <ul>
          <li>
            <NavLink to="/" onClick={handleNavLinkClick} className={({ isActive }) => (isActive ? 'active' : '')}>
              Inicio
            </NavLink>
          </li>
          <li>
            <NavLink to="/ceparium" onClick={handleNavLinkClick} className={({ isActive }) => (isActive ? 'active' : '')}>
              Ceparium
            </NavLink>
          </li>
          <li>
            <NavLink to="/ceparium/organisms" onClick={handleNavLinkClick} className={({ isActive }) => (isActive ? 'active' : '')}>
              Organismos
            </NavLink>
          </li>
          <li>
            <NavLink to="/ceparium/organisms/create" onClick={handleNavLinkClick} className={({ isActive }) => (isActive ? 'active' : '')}>
              Crear Organismo
            </NavLink>
          </li>
          {/* Puedes añadir más enlaces aquí en el futuro */}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;

