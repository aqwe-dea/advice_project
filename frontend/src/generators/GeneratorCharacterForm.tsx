import React, { useState } from 'react';
import '../App.css';

const GeneratorCharacterForm = () => {
  const [prompt, setPrompt] = useState('');
  const [image_url, setImage_url] = useState('');
  const [audio_url, setAudio_url] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ character_url: string; prompt: string } | null>(null);
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
      
      const response = await fetch('/generate-character/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt, image_url, audio_url })
      });
      
      clearInterval(progressInterval);
      setProgress(100);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Ошибка при генерации персонажа');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка при генерации персонажа');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateAgain = () => {
    setResult(null);
    setPrompt('');
    setImage_url('');
    setAudio_url('');
    setError(null);
  };

  return (
    <div className="character-generation">
      <h2>Создание профессионального персонажа</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      {!result ? (
        <form onSubmit={handleSubmit} className="prompt">
          <div className="form-group">
            <label htmlFor="prompt">Описание персонажа *</label>
            <textarea
              id="prompt"
              name="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Опишите вашего персонажа (например: 'Красивая девушка')"
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
          <div className="form-group">
            <label htmlFor="audio_url">УРЛ адрес вашего голоса *</label>
            <textarea
              id="audio_url"
              name="audio_url"
              value={audio_url}
              onChange={(e) => setAudio_url(e.target.value)}
              placeholder="здесь должен быть урл адрес вашего голоса"
              required
              rows={4}
            />
          </div>

          {isLoading && (
            <div className="progress-container">
              <div className="progress-bar" style={{ width: `${progress}%` }}></div>
              <p>Генерация персонажа: {progress}%</p>
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
                Генерируем персонажа...
              </>
            ) : (
              'Создать персонажа'
            )}
          </button>
        </form>
      ) : (
        <div className="result-container">
          <h3>Ваш сгенерированный персонаж</h3>
          
          <div className="character-container">
            <video 
              src={result.character_url}
              className="generated-character"
            />
            <p className="character-prompt">Запрос: "{result.prompt}"</p>
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
        Советница АКВИ создает профессионального персонажа с использованием передовых моделей искусственного интеллекта.
        Результаты носят рекомендательный характер и могут быть адаптированы под ваши потребности.
      </div>
    </div>
  );
};

export default GeneratorCharacterForm;