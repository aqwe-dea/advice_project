import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
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

function App() {
  const { theme, toggleTheme } = useTheme();
  return (
    <div className={`App ${theme}`}>
      <Router>
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
                </Routes>
                <AdviceForm />
                <AdviceList />
            </main>
        </Router>
    </div>
  );
}

export default App;