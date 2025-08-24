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
import MarketingStrategyForm from "./components/MarketingStrategyForm";
import TravelPlannerForm from "./components/TravelPlannerForm";
import CompetitorAnalysisForm from "./components/CompetitorAnalysisForm";
import CommunicationOptimizationForm from "./components/CommunicationOptimizationForm";

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
    <div style={{ 
      maxWidth: '100%', 
      margin: '0 auto', 
      padding: '0',
      backgroundColor: '#333333',
      color: '#f8f8f0'
    }}>
      <header style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 2rem',
        backgroundColor: '#2c3e50',
        color: 'white',
        position: 'relative',
        zIndex: 1000
      }}>
        <div style={{fontSize: '1.5rem', fontWeight: 'bold'}}>Советница АКВИ</div>
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
          {isMenuOpen ? '✕' : '☰'}
        </button>
      </header>
      <nav style={{
        display: isMenuOpen ? 'block' : 'none',
        position: 'fixed',
        top: '60px',
        left: '0',
        right: '0',
        bottom: '0',
        backgroundColor: 'rgba(44, 62, 80, 0.95)',
        padding: '1.5rem',
        overflowY: 'auto',
        zIndex: 999,
        boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)'
      }}>
        <ul style={{listStyle: 'none', padding: '0', margin: '0'}}>
          <li style={{marginBottom: '1.2rem'}}>
            <Link to="/" onClick={handleLinkClick} style={{
              color: isActive('/') ? 'white' : 'rgba(255, 255, 255, 0.85)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.8rem 1rem',
              borderRadius: '8px',
              backgroundColor: isActive('/') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: isActive('/') ? 'bold' : 'normal',
              transition: 'all 0.2s'
            }}>Главная</Link>
          </li>
          <li style={{marginBottom: '1.2rem'}}>
            <Link to="/course" onClick={handleLinkClick} style={{
              color: isActive('/course') ? 'white' : 'rgba(255, 255, 255, 0.85)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.8rem 1rem',
              borderRadius: '8px',
              backgroundColor: isActive('/course') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: isActive('/course') ? 'bold' : 'normal',
              transition: 'all 0.2s'
            }}>Курсы</Link>
          </li>
          <li style={{marginBottom: '1.2rem'}}>
            <Link to="/legal-document-analysis" onClick={handleLinkClick} style={{
              color: isActive('/legal-document-analysis') ? 'white' : 'rgba(255, 255, 255, 0.85)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.8rem 1rem',
              borderRadius: '8px',
              backgroundColor: isActive('/legal-document-analysis') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: isActive('/legal-document-analysis') ? 'bold' : 'normal',
              transition: 'all 0.2s'
            }}>Юридический анализ</Link>
          </li>
          <li style={{marginBottom: '1.2rem'}}>
            <Link to="/financial-analysis" onClick={handleLinkClick} style={{
              color: isActive('/financial-analysis') ? 'white' : 'rgba(255, 255, 255, 0.85)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.8rem 1rem',
              borderRadius: '8px',
              backgroundColor: isActive('/financial-analysis') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: isActive('/financial-analysis') ? 'bold' : 'normal',
              transition: 'all 0.2s'
            }}>Финансовый анализ</Link>
          </li>
          <li style={{marginBottom: '1.2rem'}}>
            <Link to="/photo-restoration" onClick={handleLinkClick} style={{
              color: isActive('/photo-restoration') ? 'white' : 'rgba(255, 255, 255, 0.85)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.8rem 1rem',
              borderRadius: '8px',
              backgroundColor: isActive('/photo-restoration') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: isActive('/photo-restoration') ? 'bold' : 'normal',
              transition: 'all 0.2s'
            }}>Реставрация фото</Link>
          </li>
          <li style={{marginBottom: '1.2rem'}}>
            <Link to="/medical-image-analysis" onClick={handleLinkClick} style={{
              color: isActive('/medical-image-analysis') ? 'white' : 'rgba(255, 255, 255, 0.85)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.8rem 1rem',
              borderRadius: '8px',
              backgroundColor: isActive('/medical-image-analysis') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: isActive('/medical-image-analysis') ? 'bold' : 'normal',
              transition: 'all 0.2s'
            }}>Медицинский анализ</Link>
          </li>
          <li style={{marginBottom: '1.2rem'}}>
            <Link to="/three-d-model-converter" onClick={handleLinkClick} style={{
              color: isActive('/three-d-model-converter') ? 'white' : 'rgba(255, 255, 255, 0.85)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.8rem 1rem',
              borderRadius: '8px',
              backgroundColor: isActive('/three-d-model-converter') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: isActive('/three-d-model-converter') ? 'bold' : 'normal',
              transition: 'all 0.2s'
            }}>3D-модели</Link>
          </li>
          <li style={{marginBottom: '1.2rem'}}>
            <Link to="/business-plan" onClick={handleLinkClick} style={{
              color: isActive('/business-plan') ? 'white' : 'rgba(255, 255, 255, 0.85)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.8rem 1rem',
              borderRadius: '8px',
              backgroundColor: isActive('/business-plan') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: isActive('/business-plan') ? 'bold' : 'normal',
              transition: 'all 0.2s'
            }}>Бизнес-планы</Link>
          </li>
          <li style={{marginBottom: '1.2rem'}}>
            <Link to="/presentation" onClick={handleLinkClick} style={{
              color: isActive('/presentation') ? 'white' : 'rgba(255, 255, 255, 0.85)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.8rem 1rem',
              borderRadius: '8px',
              backgroundColor: isActive('/presentation') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: isActive('/presentation') ? 'bold' : 'normal',
              transition: 'all 0.2s'
            }}>Презентации</Link>
          </li>
          <li style={{marginBottom: '1.2rem'}}>
            <Link to="/health-recommendation" onClick={handleLinkClick} style={{
              color: isActive('/health-recommendation') ? 'white' : 'rgba(255, 255, 255, 0.85)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.8rem 1rem',
              borderRadius: '8px',
              backgroundColor: isActive('/health-recommendation') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: isActive('/health-recommendation') ? 'bold' : 'normal',
              transition: 'all 0.2s'
            }}>Здоровье</Link>
          </li>
          <li style={{marginBottom: '1.2rem'}}>
            <Link to="/investment-analysis" onClick={handleLinkClick} style={{
              color: isActive('/investment-analysis') ? 'white' : 'rgba(255, 255, 255, 0.85)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.8rem 1rem',
              borderRadius: '8px',
              backgroundColor: isActive('/investment-analysis') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: isActive('/investment-analysis') ? 'bold' : 'normal',
              transition: 'all 0.2s'
            }}>Инвестиции</Link>
          </li>
          <li style={{marginBottom: '1.2rem'}}>
            <Link to="/marketing-strategy" onClick={handleLinkClick} style={{
              color: isActive('/marketing-strategy') ? 'white' : 'rgba(255, 255, 255, 0.85)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.8rem 1rem',
              borderRadius: '8px',
              backgroundColor: isActive('/marketing-strategy') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: isActive('/marketing-strategy') ? 'bold' : 'normal',
              transition: 'all 0.2s'
            }}>Стратегия продвижения</Link>
          </li>
          <li style={{marginBottom: '1.2rem'}}>
            <Link to="/travel-planner" onClick={handleLinkClick} style={{
              color: isActive('/travel-planner') ? 'white' : 'rgba(255, 255, 255, 0.85)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.8rem 1rem',
              borderRadius: '8px',
              backgroundColor: isActive('/travel-planner') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: isActive('/travel-planner') ? 'bold' : 'normal',
              transition: 'all 0.2s'
            }}>Планировщик путешествий</Link>
          </li>
          <li style={{marginBottom: '1.2rem'}}>
            <Link to="/competitor-analysis" onClick={handleLinkClick} style={{
              color: isActive('/competitor-analysis') ? 'white' : 'rgba(255, 255, 255, 0.85)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.8rem 1rem',
              borderRadius: '8px',
              backgroundColor: isActive('/competitor-analysis') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: isActive('/competitor-analysis') ? 'bold' : 'normal',
              transition: 'all 0.2s'
            }}>Анализ конкурентов</Link>
          </li>
          <li style={{marginBottom: '1.2rem'}}>
            <Link to="/communication-optimization" onClick={handleLinkClick} style={{
              color: isActive('/communication-optimization') ? 'white' : 'rgba(255, 255, 255, 0.85)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.8rem 1rem',
              borderRadius: '8px',
              backgroundColor: isActive('/communication-optimization') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: isActive('/communication-optimization') ? 'bold' : 'normal',
              transition: 'all 0.2s'
            }}>Оптимизация коммуникации</Link>
          </li>
          <li style={{marginBottom: '1.2rem'}}>
            <Link to="/about" onClick={handleLinkClick} style={{
              color: isActive('/about') ? 'white' : 'rgba(255, 255, 255, 0.85)',
              textDecoration: 'none', 
              display: 'block', 
              padding: '0.8rem 1rem',
              borderRadius: '8px',
              backgroundColor: isActive('/about') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              fontWeight: isActive('/about') ? 'bold' : 'normal',
              transition: 'all 0.2s'
            }}>О проекте</Link>
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
          <Route path="/marketing-strategy" element={<MarketingStrategyForm />} />
          <Route path="/travel-planner" element={<TravelPlannerForm />} />
          <Route path="/competitor-analysis" element={<CompetitorAnalysisForm />} />
          <Route path="/communication-optimization" element={<CommunicationOptimizationForm />} />
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