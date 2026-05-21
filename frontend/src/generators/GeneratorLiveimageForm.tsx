import React, { useState, useEffect } from 'react';
import '../App.css';

const GeneratorLiveimageForm = () => {
  const [prompt, setPrompt] = useState('');
  const [image_url, setImage_url] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ liveimage_url: string; prompt: string } | null>(null);
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
      
      const response = await fetch('/generate-liveimage/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt, image_url })
      });
      
      clearInterval(progressInterval);
      setProgress(100);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Ошибка при генерации живого изображения');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка при генерации живого изображения');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateAgain = () => {
    setResult(null);
    setPrompt('');
    setImage_url('');
    setError(null);
  };

  return (
    <div className="liveimage-generation">
      <h2>Создание профессионального живого изображения</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      {!result ? (
        <form onSubmit={handleSubmit} className="prompt">
          <div className="form-group">
            <label htmlFor="prompt">Описание живого изображения *</label>
            <textarea
              id="prompt"
              name="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Опишите, что вы хотите услышать (например: 'Магический кристалл любви')"
              required
              rows={4}
            />
          </div>
          <div className="form-group">
            <label htmlFor="image_url">УРЛ адрес вашего изображения *</label>
            <textarea
              id="image_url"
              name="image_url"
              value={image_url}
              onChange={(e) => setImage_url(e.target.value)}
              placeholder="здесь должен быть урл адрес вашего изображения"
              required
              rows={4}
            />
          </div>
          
          {isLoading && (
            <div className="progress-container">
              <div className="progress-bar" style={{ width: `${progress}%` }}></div>
              <p>Генерация живого изображения: {progress}%</p>
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
                Генерируем живое изображение...
              </>
            ) : (
              'Создать живое изображение'
            )}
          </button>
        </form>
      ) : (
        <div className="result-container">
          <h3>Ваше живое изображение</h3>
          
          <div className="liveimage-container">
            <img 
              src={result.liveimage_url} 
              alt="Сгенерированное живое изображение" 
              className="generated-liveimage"
            />
            <p className="liveimage-prompt">Запрос: "{result.prompt}"</p>
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
        Советница АКВИ создает профессиональное живое изображение с использованием передовых моделей искусственного интеллекта.
        Результаты носят рекомендательный характер и могут быть адаптированы под ваши потребности.
      </div>
    </div>
  );
};

export default GeneratorLiveimageForm;