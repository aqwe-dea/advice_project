import React, { useState } from 'react';
import '../App.css';
import ReactMarkdown from 'react-markdown';

const API_BASE_URL = 'http://127.0.0.1:8000';
const MEDIA_URL = `${API_BASE_URL}/media/`;

const ThreeDModelConverterForm = () => {
  const [formData, setFormData] = useState({
    idea: '',
    model_type: 'персонаж',
    software: 'Blender, Maya, ZBrush',
    complexity: 'средняя',
    purpose: 'визуализация, анимация',
    timeframe: '2-4 недели'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [progress, setProgress] = useState(0);
  const [imageLoaded, setImageLoaded] = useState(false);
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.idea.trim()) {
      setError('Пожалуйста, укажите идею 3D-модели');
      return;
    }
    setIsLoading(true);
    setError(null);
    setResult(null);
    setProgress(0);
    setImageLoaded(false);
    try {
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 95) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 5;
        });
      }, 300);
      const response = await fetch(`${API_BASE_URL}/3d-to-project/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      clearInterval(progressInterval);
      setProgress(100);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Ошибка при генерации плана 3D-моделирования');
      }
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка при генерации плана 3D-моделирования');
    } finally {
      setIsLoading(false);
    }
  };
  const getFullImageUrl = (relativeUrl: string | null) => {
    if (!relativeUrl) return null;
    if (relativeUrl.startsWith('http://') || relativeUrl.startsWith('https://')) {
      return relativeUrl;
    }
    return `${MEDIA_URL}${relativeUrl.replace('/media/', '')}`;
  };
  const extractSection = (text: string, startMarker: string, endMarker: string | null): string => {
    const startIndex = text.indexOf(startMarker);
    if (startIndex === -1) return "";
    let endIndex = -1;
    if (endMarker) {
      endIndex = text.indexOf(endMarker, startIndex + startMarker.length);
    }
    if (endIndex === -1) {
      return text.substring(startIndex + startMarker.length).trim();
    }
    return text.substring(startIndex + startMarker.length, endIndex).trim();
  };
  const renderModelingPlan = () => {
    if (!result || !result.modeling_plan) return null;
    const imageUrl = getFullImageUrl(result.image3dmodel);
    
    return (
      <div className="modeling-plan">
        <h3>План 3D-моделирования: {formData.model_type}</h3>
        {imageUrl && (
          <div className="model-image-container">
            <h4>Визуализация 3D-модели</h4>
            {!imageLoaded && (
              <div className="image-loader">Загрузка изображения 3D-модели...</div>
            )}
            <img 
              src={imageUrl} 
              alt={`3D модель: ${formData.idea}`}
              className="model-image"
              onLoad={() => setImageLoaded(true)}
              style={{ 
                display: imageLoaded ? 'block' : 'none',
                maxWidth: '100%',
                maxHeight: '500px',
                margin: '20px auto',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
              }}
            />
          </div>
        )}
        <div className="plan-text">
          <ReactMarkdown>{result.modeling_plan}</ReactMarkdown>
        </div>
        <button 
          onClick={() => setResult(null)}
          className="reset-button"
        >
          Сгенерировать новый план
        </button>
      </div>
    );
  };
  return (
    <div className="modeling-container">
      <h2>План 3D-моделирования</h2>
      <p>Заполните форму для создания структурированного плана по созданию 3D-модели</p>
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      {!result ? (
        <form onSubmit={handleSubmit} className="modeling-form">
          <div className="form-group">
            <label htmlFor="idea">Идея модели *</label>
            <textarea
              id="idea"
              name="idea"
              value={formData.idea}
              onChange={handleChange}
              placeholder="Опишите идею вашей 3D-модели"
              rows={4}
              required
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="model_type">Тип модели</label>
              <select
                id="model_type"
                name="model_type"
                value={formData.model_type}
                onChange={handleChange}
              >
                <option value="персонаж">Персонаж</option>
                <option value="объект">Объект</option>
                <option value="среда">Среда/Локация</option>
                <option value="транспорт">Транспорт</option>
                <option value="архитектура">Архитектура</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="complexity">Сложность</label>
              <select
                id="complexity"
                name="complexity"
                value={formData.complexity}
                onChange={handleChange}
              >
                <option value="низкая">Низкая</option>
                <option value="средняя">Средняя</option>
                <option value="высокая">Высокая</option>
                <option value="очень высокая">Очень высокая</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="software">Программное обеспечение</label>
            <input
              type="text"
              id="software"
              name="software"
              value={formData.software}
              onChange={handleChange}
              placeholder="Например: Blender, Maya, ZBrush"
            />
          </div>
          <div className="form-group">
            <label htmlFor="purpose">Цель модели</label>
            <input
              type="text"
              id="purpose"
              name="purpose"
              value={formData.purpose}
              onChange={handleChange}
              placeholder="Например: визуализация, анимация, игра, VR"
            />
          </div>
          <div className="form-group">
            <label htmlFor="timeframe">Временные рамки</label>
            <input
              type="text"
              id="timeframe"
              name="timeframe"
              value={formData.timeframe}
              onChange={handleChange}
              placeholder="Например: 2-4 недели"
            />
          </div>
          <button 
            type="submit" 
            className="generate-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Генерируем план 3D-моделирования...
              </>
            ) : (
              'Сгенерировать план'
            )}
          </button>
        </form>
      ) : (
        renderModelingPlan()
      )}
      <div className="footer-note">
        Советница АКВИ создает структурированные планы по 3D-моделированию с использованием передовых моделей искусственного интеллекта. 
        Результаты носят рекомендательный характер и могут быть адаптированы под ваши потребности.
      </div>
    </div>
  );
};

export default ThreeDModelConverterForm;