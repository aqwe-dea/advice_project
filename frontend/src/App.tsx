import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
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

function App() {
  const { theme, toggleTheme } = useTheme();
  return (
    <div className={`App ${theme}`}>
      <Router>
        <div className="app-container" style={{maxWidth: '1400px', margin: '0 auto', padding: '0'}}>
        <nav style={{
          display: 'flex', 
          justifyContent: 'center',
          gap: '2rem',
          padding: '1.5rem 0',
          backgroundColor: '#2c3e50',
          color: 'white'
        }}>
          <Link to="/chat" style={{color: 'white', textDecoration: 'none', fontWeight: 'bold'}}>Главная</Link>
          <Link to="/course" style={{color: 'white', textDecoration: 'none'}}>Курсы</Link>
          <Link to="/legal-document-analysis" style={{color: 'white', textDecoration: 'none'}}>Юр. анализ</Link>
          <Link to="/financial-analysis" style={{color: 'white', textDecoration: 'none'}}>Фин. анализ</Link>
          <Link to="/photo-restoration" style={{color: 'white', textDecoration: 'none'}}>Фото</Link>
          <Link to="/medical-image-analysis" style={{color: 'white', textDecoration: 'none'}}>Мед. анализ</Link>
          <Link to="/three-d-model-converter" style={{color: 'white', textDecoration: 'none'}}>3D-модели</Link>
          <Link to="/business-plan" style={{color: 'white', textDecoration: 'none'}}>Бизнес-план</Link>
          <Link to="/presentation" style={{color: 'white', textDecoration: 'none'}}>Презентации</Link>
          <Link to="/health-recommendation" style={{color: 'white', textDecoration: 'none'}}>Здоровье</Link>
          <Link to="/investment-analysis" style={{color: 'white', textDecoration: 'none'}}>Инвестиции</Link>
        </nav>
        </div>
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
      </Router>
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

export default App;