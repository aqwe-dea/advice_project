import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { useTheme } from './contexts/ThemeContext';
import logo from '../src/logo.svg';
import './App.css';
import Home from 'components/Home';
import About from 'components/About';
import AdviceList from './components/AdviceList';
import AdviceForm from './components/AdviceForm';
import Notification from './components/Notification';
import Navbar from 'components/Navbar';


function App() {
  const { theme, toggleTheme } = useTheme();
  const [notificationMessage, setNotificationMessage] = useState('');
  const showNotification = (message: string) => {
    setNotificationMessage(message);
    setTimeout(() => setNotificationMessage(''), 3000);
  };
 
  return (
    <Router>
     <div className={`App ${theme}`}>
       <Navbar />
      <header className="App-header">
         <h1>Советница АКВИ</h1>
        <button onClick={toggleTheme}>
          {theme === 'light' ? 'Переключить на темную тему' : 'Переключить на светлую тему'}
        </button>
         <img src={logo} className="App-logo" alt="logo" />
      </header>
      <main>
        <AdviceForm onSuccess={() => showNotification('Вопрос успешно отправлен!')} />
        <AdviceList />
      </main>
       <Routes>
         <Route path="/" element={<Home />} />
         <Route path="/about" element={<About />} />
       </Routes>
       {notificationMessage && (
        <Notification
        message={notificationMessage}
        onClose={() => setNotificationMessage('')}/>
       )}
     </div>
    </Router>
  );
}


export default App;
