import React, { useState, useEffect } from 'react';
import '../App.css';

const GeneratorCodeForm = () => {
  const [prompt, setPrompt] = useState('');
  const [language, setLanguage] = useState('python');
  const [include_comments, setInclude_comments] = useState('True');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ code: string; prompt: string } | null>(null);
  const [progress, setProgress] = useState(0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) {
      setError('Пожалуйста, введите текст для генерации');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setResult(null);
    setProgress(0);
    
    try {
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 95) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 3;
        });
      }, 200);
      
      const response = await fetch('/generate-code/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt, language, include_comments })
      });
      
      clearInterval(progressInterval);
      setProgress(100);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Ошибка при генерации кода');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка при генерации кода');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateAgain = () => {
    setResult(null);
    setPrompt('');
    setLanguage('python');
    setInclude_comments('True');
    setError(null);
  };

  return (
    <div className="code-generation">
      <h2>Создание профессионального кода</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      {!result ? (
        <form onSubmit={handleSubmit} className="prompt">
          <div className="form-group">
            <label htmlFor="prompt">Описание кода *</label>
            <textarea
              id="prompt"
              name="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Опишите какой код вам нужен (например: 'Функция или скрипт')"
              required
              rows={4}
            />
          </div>
          <div className="form-group">
            <label htmlFor="language">language, python *</label>
            <textarea
              id="language"
              name="language"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              placeholder="language, python"
              required
              rows={4}
            />
          </div>
          <div className="form-group">
            <label htmlFor="include_comments">'include_comments', True *</label>
            <textarea
              id="include_comments"
              name="include_comments"
              value={include_comments}
              onChange={(e) => setInclude_comments(e.target.value)}
              placeholder="include_comments, True"
              required
              rows={4}
            />
          </div>

          {isLoading && (
            <div className="progress-container">
              <div className="progress-bar" style={{ width: `${progress}%` }}></div>
              <p>Генерация кода: {progress}%</p>
            </div>
          )}
          
          <button 
            type="submit" 
            className="generate-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Генерируем код...
              </>
            ) : (
              'Создать код'
            )}
          </button>
        </form>
      ) : (
        <div className="result-container">
          <h3>Ваш сгенерированный код</h3>
          
          <div className="code-container">
            <p className="generated-code">
            Ваш код: "{result.code}"  
            </p>
            <p className="code-prompt">Запрос: "{result.prompt}"</p>
          </div>
          
          <div className="action-buttons">
            <button 
              onClick={handleGenerateAgain}
              className="generate-again-button"
            >
              Сгенерировать ещё
            </button>
          </div>
        </div>
      )}
      
      <div className="footer-note">
        Советница АКВИ создает профессиональный код с использованием передовых моделей искусственного интеллекта.
        Результаты носят рекомендательный характер и могут быть адаптированы под ваши потребности.
      </div>
    </div>
  );
};

export default GeneratorCodeForm;