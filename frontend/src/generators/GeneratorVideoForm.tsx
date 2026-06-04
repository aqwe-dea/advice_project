import React, { useState, useEffect } from 'react';
import '../App.css';

const GeneratorVideoForm = () => {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ video_url: string; prompt: string } | null>(null);
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
      
      const response = await fetch('/generate-video/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt })
      });
      
      clearInterval(progressInterval);
      setProgress(100);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Ошибка при генерации видео');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка при генерации видео');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateAgain = () => {
    setResult(null);
    setPrompt('');
    setError(null);
  };

  return (
    <div className="video-generation">
      <h2>Создание профессионального видео</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      {!result ? (
        <form onSubmit={handleSubmit} className="prompt">
          <div className="form-group">
            <label htmlFor="prompt">Описание видео *</label>
            <textarea
              id="prompt"
              name="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Опишите, что вы хотите увидеть (например: 'Магический кристалл любви, фиолетовый свет, космический фон')"
              required
              rows={4}
            />
          </div>
          
          {isLoading && (
            <div className="progress-container">
              <div className="progress-bar" style={{ width: `${progress}%` }}></div>
              <p>Генерация видео: {progress}%</p>
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
                Генерируем видео...
              </>
            ) : (
              'Создать видео'
            )}
          </button>
        </form>
      ) : (
        <div className="result-container">
          <h3>Ваше сгенерированное видео</h3>
          
          <div className="video-container">
            <video 
              src={result.video_url}
              className="generated-video"
            />
            <p className="video-prompt">Запрос: "{result.prompt}"</p>
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
        Советница АКВИ создает профессиональные видео с использованием передовых моделей искусственного интеллекта.
        Результаты носят рекомендательный характер и могут быть адаптированы под ваши потребности.
      </div>
    </div>
  );
};

export default GeneratorVideoForm;