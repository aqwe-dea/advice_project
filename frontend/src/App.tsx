import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { useLocation } from 'react-router-dom';
import { useTheme } from './contexts/ThemeContext';
import logo from '../src/logo.svg';
import './App.css';
import Home from './components/Home';
import About from './components/About';
import Sovet from './components/Sovet';
import DetailedAdviceForm from './components/DetailedAdviceForm';
import AdviceList from './components/AdviceList';
import AdviceForm from './components/AdviceForm';
import Navbar from './components/Navbar';
import Chat from './components/Chat';
import StripeDonation from './components/StripeDonation';
import CourseForm from "./components/CourseForm";
import LegalDocumentAnalysisForm from "./components/LegalDocumentAnalysisForm";
import FinancialAnalysisForm from "./components/FinancialAnalysisForm";
import PhotoRestorationForm from "./components/PhotoRestorationForm";
import MedicalImageAnalysisForm from "./components/MedicalImageAnalysisForm";
import ThreeDModelConverterForm from "./components/ThreeDModelConverterForm";
import HealthRecommendationForm from "./components/HealthRecommendationForm";
import BusinessPlanForm from "./components/BusinessPlanForm";
import PresentationForm from "./components/PresentationForm";
import InvestmentAnalysisForm from "./components/InvestmentAnalysisForm";

function AppContent() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();
  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };
  const handleLinkClick = () => {
    setIsMenuOpen(false);
  };
  const isActive = (path: string) => {
    return location.pathname === path;
  };
  const { theme, toggleTheme } = useTheme();
  return (
    <div className={`App ${theme}`}>
      <div style={{ maxWidth: '100%', margin: '0 auto', padding: '0' }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem',
        backgroundColor: '#2c3e50',
        color: 'white',
        position: 'relative',
        zIndex: 1000
      }}>
      </div>
        <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>Советница АКВИ</div>
        <button 
          onClick={toggleMenu}
          style={{
            background: 'none',
            border: 'none',
            color: 'white',
            fontSize: '1.5rem',
            cursor: 'pointer',
            display: 'block'
          }}
        >
          ☰
        </button>
      </div>
      <nav style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '2rem',
        padding: '1.5rem 0',
        backgroundColor: '#2c3e50',
        color: 'white'
      }} className="desktop-nav">
        <Link to="/" style={{
          color: isActive('/') ? 'white' : 'rgba(255, 255, 255, 0.7)',
          textDecoration: 'none', 
          fontWeight: isActive('/') ? 'bold' : 'normal'
        }}>Главная</Link>
        <Link to="/course" style={{
          color: isActive('/course') ? 'white' : 'rgba(255, 255, 255, 0.7)',
          textDecoration: 'none', 
          fontWeight: isActive('/course') ? 'bold' : 'normal'
        }}>Курсы</Link>
        <Link to="/legal-document-analysis" style={{
          color: isActive('/legal-document-analysis') ? 'white' : 'rgba(255, 255, 255, 0.7)',
          textDecoration: 'none', 
          fontWeight: isActive('/legal-document-analysis') ? 'bold' : 'normal'
        }}>Юр. анализ</Link>
        <Link to="/financial-analysis" style={{
          color: isActive('/financial-analysis') ? 'white' : 'rgba(255, 255, 255, 0.7)',
          textDecoration: 'none', 
          fontWeight: isActive('/financial-analysis') ? 'bold' : 'normal'
        }}>Фин. анализ</Link>
        <Link to="/photo-restoration" style={{
          color: isActive('/photo-restoration') ? 'white' : 'rgba(255, 255, 255, 0.7)',
          textDecoration: 'none', 
          fontWeight: isActive('/photo-restoration') ? 'bold' : 'normal'
        }}>Фото</Link>
        <Link to="/medical-image-analysis" style={{
          color: isActive('/medical-image-analysis') ? 'white' : 'rgba(255, 255, 255, 0.7)',
          textDecoration: 'none', 
          fontWeight: isActive('/medical-image-analysis') ? 'bold' : 'normal'
        }}>Мед. анализ</Link>
        <Link to="/three-d-model-converter" style={{
          color: isActive('/three-d-model-converter') ? 'white' : 'rgba(255, 255, 255, 0.7)',
          textDecoration: 'none', 
          fontWeight: isActive('/three-d-model-converter') ? 'bold' : 'normal'
        }}>3D-модели</Link>
        <Link to="/business-plan" style={{
          color: isActive('/business-plan') ? 'white' : 'rgba(255, 255, 255, 0.7)',
          textDecoration: 'none', 
          fontWeight: isActive('/business-plan') ? 'bold' : 'normal'
        }}>Бизнес-план</Link>
        <Link to="/presentation" style={{
          color: isActive('/presentation') ? 'white' : 'rgba(255, 255, 255, 0.7)',
          textDecoration: 'none', 
          fontWeight: isActive('/presentation') ? 'bold' : 'normal'
        }}>Презентации</Link>
        <Link to="/health-recommendation" style={{
          color: isActive('/health-recommendation') ? 'white' : 'rgba(255, 255, 255, 0.7)',
          textDecoration: 'none', 
          fontWeight: isActive('/health-recommendation') ? 'bold' : 'normal'
        }}>Здоровье</Link>
        <Link to="/investment-analysis" style={{
          color: isActive('/investment-analysis') ? 'white' : 'rgba(255, 255, 255, 0.7)',
          textDecoration: 'none', 
          fontWeight: isActive('/investment-analysis') ? 'bold' : 'normal'
        }}>Инвестиции</Link>
      </nav>
      <nav style={{
        display: isMenuOpen ? 'block' : 'none',
        position: 'absolute',
        top: '60px',
        left: '0',
        right: '0',
        backgroundColor: '#2c3e50',
        padding: '1rem',
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
        zIndex: 999
      }} className="mobile-nav">
        <ul style={{ listStyle: 'none', padding: '0', margin: '0' }}>
          <li style={{ marginBottom: '1rem' }}>
            <Link to="/" onClick={handleLinkClick} style={{
              color: isActive('/') ? 'white' : 'rgba(255, 255, 255, 0.7)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.5rem',
              fontWeight: isActive('/') ? 'bold' : 'normal'
            }}>Главная</Link>
          </li>
          <li style={{ marginBottom: '1rem' }}>
            <Link to="/course" onClick={handleLinkClick} style={{
              color: isActive('/course') ? 'white' : 'rgba(255, 255, 255, 0.7)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.5rem',
              fontWeight: isActive('/course') ? 'bold' : 'normal'
            }}>Курсы</Link>
          </li>
          <li style={{ marginBottom: '1rem' }}>
            <Link to="/legal-document-analysis" onClick={handleLinkClick} style={{
              color: isActive('/legal-document-analysis') ? 'white' : 'rgba(255, 255, 255, 0.7)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.5rem',
              fontWeight: isActive('/legal-document-analysis') ? 'bold' : 'normal'
            }}>Юр. анализ</Link>
          </li>
          <li style={{ marginBottom: '1rem' }}>
            <Link to="/financial-analysis" onClick={handleLinkClick} style={{
              color: isActive('/financial-analysis') ? 'white' : 'rgba(255, 255, 255, 0.7)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.5rem',
              fontWeight: isActive('/financial-analysis') ? 'bold' : 'normal'
            }}>Фин. анализ</Link>
          </li>
          <li style={{ marginBottom: '1rem' }}>
            <Link to="/photo-restoration" onClick={handleLinkClick} style={{
              color: isActive('/photo-restoration') ? 'white' : 'rgba(255, 255, 255, 0.7)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.5rem',
              fontWeight: isActive('/photo-restoration') ? 'bold' : 'normal'
            }}>Фото</Link>
          </li>
          <li style={{ marginBottom: '1rem' }}>
            <Link to="/medical-image-analysis" onClick={handleLinkClick} style={{
              color: isActive('/medical-image-analysis') ? 'white' : 'rgba(255, 255, 255, 0.7)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.5rem',
              fontWeight: isActive('/medical-image-analysis') ? 'bold' : 'normal'
            }}>Мед. анализ</Link>
          </li>
          <li style={{ marginBottom: '1rem' }}>
            <Link to="/three-d-model-converter" onClick={handleLinkClick} style={{
              color: isActive('/three-d-model-converter') ? 'white' : 'rgba(255, 255, 255, 0.7)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.5rem',
              fontWeight: isActive('/three-d-model-converter') ? 'bold' : 'normal'
            }}>3D-модели</Link>
          </li>
          <li style={{ marginBottom: '1rem' }}>
            <Link to="/business-plan" onClick={handleLinkClick} style={{
              color: isActive('/business-plan') ? 'white' : 'rgba(255, 255, 255, 0.7)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.5rem',
              fontWeight: isActive('/business-plan') ? 'bold' : 'normal'
            }}>Бизнес-план</Link>
          </li>
          <li style={{ marginBottom: '1rem' }}>
            <Link to="/presentation" onClick={handleLinkClick} style={{
              color: isActive('/presentation') ? 'white' : 'rgba(255, 255, 255, 0.7)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.5rem',
              fontWeight: isActive('/presentation') ? 'bold' : 'normal'
            }}>Презентации</Link>
          </li>
          <li style={{ marginBottom: '1rem' }}>
            <Link to="/health-recommendation" onClick={handleLinkClick} style={{
              color: isActive('/health-recommendation') ? 'white' : 'rgba(255, 255, 255, 0.7)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.5rem',
              fontWeight: isActive('/health-recommendation') ? 'bold' : 'normal'
            }}>Здоровье</Link>
          </li>
          <li style={{ marginBottom: '1rem' }}>
            <Link to="/investment-analysis" onClick={handleLinkClick} style={{
              color: isActive('/investment-analysis') ? 'white' : 'rgba(255, 255, 255, 0.7)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.5rem',
              fontWeight: isActive('/investment-analysis') ? 'bold' : 'normal'
            }}>Инвестиции</Link>
          </li>
        </ul>
      </nav>
      <Navbar />
      <header className="App-header">
        <h1>Советница АКВИ</h1>
          <button onClick={toggleTheme}>
            {theme === 'light' ? 'Переключить на темную тему' : 'Переключить на светлую тему'}
          </button>
          <img src={logo} className="App-logo" alt="logo" />
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/sovet" element={<Sovet />} />
          <Route path="/detailed-advice" element={<DetailedAdviceForm />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/donation" element={<StripeDonation />} />
          <Route path="/course" element={<CourseForm />} />
          <Route path="/legal-document-analysis" element={<LegalDocumentAnalysisForm />} />
          <Route path="/financial-analysis" element={<FinancialAnalysisForm />} />
          <Route path="/photo-restoration" element={<PhotoRestorationForm />} />
          <Route path="/medical-image-analysis" element={<MedicalImageAnalysisForm />} />
          <Route path="/three-d-model-converter" element={<ThreeDModelConverterForm />} />
          <Route path="/health-recommendation" element={<HealthRecommendationForm />} />
          <Route path="/business-plan" element={<BusinessPlanForm />} />
          <Route path="/presentation" element={<PresentationForm />} />
          <Route path="/investment-analysis" element={<InvestmentAnalysisForm />} />
        </Routes>
        <AdviceForm />
        <AdviceList />
      </main>
     <footer style={{
      marginTop: '3rem',
      paddingTop: '2rem',
      borderTop: '1px solid #e0e0e0',
      textAlign: 'center',
      color: '#7f8c8d',
      fontSize: '0.9rem'
     }}>
     <p>© 2023 Советница АКВИ. Все права защищены.</p>
     <div style={{display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '1rem'}}>
     <a href="/about" style={{color: '#3498db', textDecoration: 'none'}}>О проекте</a>
     <a href="/privacy" style={{color: '#3498db', textDecoration: 'none'}}>Политика конфиденциальности</a>
     <a href="/terms" style={{color: '#3498db', textDecoration: 'none'}}>Условия использования</a>
     </div>
     </footer>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;