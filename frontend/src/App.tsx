import { useState } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import OrganismListPage from './pages/OrganismListPage';
import OrganismDetailPage from './pages/OrganismDetailPage';
import OrganismFormPage from './pages/OrganismFormPage';
import StrainFormPage from './pages/StrainFormPage';
import StrainAnalysisPage from './pages/StrainAnalysisPage';
import CepariumPage from './pages/CepariumPage';
import AnalysisListPage from './pages/AnalysisListPage';
import UserAnalysisPage from './pages/UserAnalysisPage';
import HomePage from './pages/HomePage';
import StrainCreatePage from './pages/StrainCreatePage';
import IndividualFileUploadPage from './pages/IndividualFileUploadPage';
import Sidebar from './components/Sidebar'; // Importar el nuevo Sidebar

function App() {
  const [isSidebarOpen, setSidebarOpen] = useState(false);

  return (
    <Router>
      <div className="App">
        <button className="menu-button" onClick={() => setSidebarOpen(true)}>
          ☰
        </button>
        <Sidebar isOpen={isSidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="main-content">
          <Routes>
            <Route path="/ceparium" element={<CepariumPage />} />
            <Route path="/ceparium/organisms" element={<OrganismListPage />} />
            <Route path="/ceparium/organisms/create" element={<OrganismFormPage />} />
            <Route path="/ceparium/organisms/:id" element={<OrganismDetailPage />} />
            <Route path="/ceparium/organisms/:id/edit" element={<OrganismFormPage />} />
            <Route path="/ceparium/strains/create" element={<StrainCreatePage />} />
            <Route path="/ceparium/organisms/:organismId/strains/create" element={<StrainFormPage />} />
            <Route path="/ceparium/strains/:id/analyses" element={<StrainAnalysisPage />} />
            <Route path="/ceparium/analyses" element={<AnalysisListPage />} />
            <Route path="/ceparium/user-analyses" element={<UserAnalysisPage />} />
            <Route path="/ceparium/strains/:strainId/upload" element={<IndividualFileUploadPage />} />
            <Route path="/" element={<HomePage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
