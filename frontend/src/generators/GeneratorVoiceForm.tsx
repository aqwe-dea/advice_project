import React, { useState, useEffect } from 'react';
import '../App.css';

const GeneratorVoiceForm = () => {
  const [text, setText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ audio_url: string; text: string } | null>(null);
  const [progress, setProgress] = useState(0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) {
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
      
      const response = await fetch('/generate-voice/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text })
      });
      
      clearInterval(progressInterval);
      setProgress(100);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Ошибка при генерации голоса');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка при генерации голоса');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateAgain = () => {
    setResult(null);
    setText('');
    setError(null);
  };

  return (
    <div className="voice-generation">
      <h2>Создание профессионального голоса</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      {!result ? (
        <form onSubmit={handleSubmit} className="text">
          <div className="form-group">
            <label htmlFor="text">Описание голоса *</label>
            <textarea
              id="text"
              name="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Опишите, какой голос вы хотите услышать (например: 'приятный и милый голос')"
              required
              rows={4}
            />
          </div>
          
          {isLoading && (
            <div className="progress-container">
              <div className="progress-bar" style={{ width: `${progress}%` }}></div>
              <p>Генерация голоса: {progress}%</p>
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
                Генерируем голос...
              </>
            ) : (
              'Создать голос'
            )}
          </button>
        </form>
      ) : (
        <div className="result-container">
          <h3>Ваш голос</h3>
          
          <div className="voice-container">
            <img 
              src={result.audio_url} 
              alt="Сгенерированный голос" 
              className="generated-voice"
            />
            <p className="voice-text">Запрос: "{result.text}"</p>
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
        Советница АКВИ создает профессиональный голос с использованием передовых моделей искусственного интеллекта.
        Результаты носят рекомендательный характер и могут быть адаптированы под ваши потребности.
      </div>
    </div>
  );
};

export default GeneratorVoiceForm;