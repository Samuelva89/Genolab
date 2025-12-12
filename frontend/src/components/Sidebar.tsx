import React from 'react';
import { NavLink } from 'react-router-dom';
import { FaHome, FaDna, FaMicroscope, FaPlus, FaChartBar, FaTimes } from 'react-icons/fa';
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
        <h2>GENOLAB</h2>
        <button className="sidebar-close-button" onClick={onClose}>
          <FaTimes />
        </button>
      </div>
      <nav className="sidebar-nav">
        <ul>
          <li>
            <NavLink
              to="/"
              onClick={handleNavLinkClick}
              className={({ isActive }) => isActive ? 'active' : ''}
              end // Asegura que solo se active cuando la ruta es exacta
            >
              <FaHome className="sidebar-icon" /> Inicio
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/ceparium"
              onClick={handleNavLinkClick}
              className={({ isActive }) => isActive ? 'active' : ''}
              end // Asegura que solo se active cuando la ruta es exacta
            >
              <FaDna className="sidebar-icon" /> Ceparium
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/ceparium/organisms"
              onClick={handleNavLinkClick}
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              <FaMicroscope className="sidebar-icon" /> Organismos
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/ceparium/strains/create"
              onClick={handleNavLinkClick}
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              <FaPlus className="sidebar-icon" /> Crear Cepa
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/ceparium/organisms/create"
              onClick={handleNavLinkClick}
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              <FaPlus className="sidebar-icon" /> Crear Organismo
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/ceparium/analyses"
              onClick={handleNavLinkClick}
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              <FaChartBar className="sidebar-icon" /> Análisis
            </NavLink>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;

