import React, { useState, useEffect } from 'react';
import '../App.css';

const EditImageForm = () => {
  const [prompt, setPrompt] = useState('');
  const [input_urls, setInput_urls] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ edit_url: string; prompt: string } | null>(null);
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
      
      const response = await fetch('/image-edit/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt, input_urls })
      });
      
      clearInterval(progressInterval);
      setProgress(100);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Ошибка при редактировании изображения');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка при редактировании изображения');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateAgain = () => {
    setResult(null);
    setPrompt('');
    setInput_urls('');
    setError(null);
  };

  return (
    <div className="edit-image">
      <h2>Профессиональное редактирование изображения</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      {!result ? (
        <form onSubmit={handleSubmit} className="prompt">
          <div className="form-group">
            <label htmlFor="prompt">Как отредактировать изображения *</label>
            <textarea
              id="prompt"
              name="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Опишите, как вы хотите отредактировать изображение"
              required
              rows={4}
            />
          </div>
          <div className="form-group">
            <label htmlFor="input_urls">УРЛ адрес вашего изображения *</label>
            <textarea
              id="input_urls"
              name="input_urls"
              value={input_urls}
              onChange={(e) => setInput_urls(e.target.value)}
              placeholder="здесь должен быть урл адрес вашего изображения"
              required
              rows={4}
            />
          </div>
          
          {isLoading && (
            <div className="progress-container">
              <div className="progress-bar" style={{ width: `${progress}%` }}></div>
              <p>Редактирование изображения: {progress}%</p>
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
                Редактируем изображение...
              </>
            ) : (
              'Отредактировать изображение'
            )}
          </button>
        </form>
      ) : (
        <div className="result-container">
          <h3>Ваше отредактированное изображение</h3>
          
          <div className="editimage-container">
            <img 
              src={result.edit_url} 
              alt="Сгенерированное живое изображение" 
              className="edit-image"
            />
            <p className="editimage-prompt">Запрос: "{result.prompt}"</p>
          </div>
          
          <div className="action-buttons">
            <button 
              onClick={handleGenerateAgain}
              className="generate-again-button"
            >
              Отредактировать ещё
            </button>
          </div>
        </div>
      )}
      
      <div className="footer-note">
        Советница АКВИ профессионально редактирует изображение с использованием передовых моделей искусственного интеллекта.
        Результаты носят рекомендательный характер и могут быть адаптированы под ваши потребности.
      </div>
    </div>
  );
};

export default EditImageForm;