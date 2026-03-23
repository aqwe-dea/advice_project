import React, { useState } from 'react';
import '../App.css';
import ReactMarkdown from 'react-markdown'

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://advice-project.onrender.com';
const MEDIA_URL = `${API_BASE_URL}/media/`;

const PresentationForm = () => {
  const [formData, setFormData] = useState({
    presentation_idea: '',
    presentation_description: ''
  });  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [progress, setProgress] = useState(0);
  const [imagesLoaded, setImagesLoaded] = useState<{[key: number]: boolean}>({});
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.presentation_idea.trim() || !formData.presentation_description.trim()) {
      setError('Пожалуйста, заполните все поля');
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
      }, 300);      
      const response = await fetch(`${API_BASE_URL}/generate-presentation/`, {
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
        throw new Error(errorData.error || 'Ошибка при генерации презентации');
      }      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка при генерации презентации');
    } finally {
      setIsLoading(false);
    }
  };
  const getFullImageUrl = (relativeUrl: string | null) => {
    if (!relativeUrl) return null;
    if (relativeUrl.startsWith('http://') || relativeUrl.startsWith('https://')) {
      return relativeUrl;
    }
    const cleanUrl = relativeUrl.replace(/^\/+/, '');
    return `${API_BASE_URL}/${cleanUrl}`;
  };
  
  const handleImageLoad = (slideNumber: number) => {
    setImagesLoaded(prev => ({ ...prev, [slideNumber]: true }));
  };
  const renderPresentation = () => {
    if (!result || !result.presentation) return null;        
  
    return (
      <div className="presentation-container">
        <h3>Ваша презентация: {result.presentation_idea}</h3>
        <div className="presentation-text">
          <ReactMarkdown>{result.presentation}</ReactMarkdown>
        </div>      
        {result.outcome && result.outcome.length > 0 && (
          <div className="slides-container">
            <h4>Слайды презентации</h4>
            {result.outcome.map((slide: any, index: number) => {
              const slideNumber = slide.slide_number || index + 1;
              const slideImage = getFullImageUrl(slide.image_url);
              
              return (
                <div key={slideNumber} className="slide">
                  <div className="slide-header">
                    <h4>Слайд {slideNumber}</h4>
                    {slide.prompt && (
                      <p className="slide-prompt">{slide.prompt}</p>
                    )}
                  </div>
                  <div className="slide-content">
                    {slideImage && (
                      <div className="slide-image">
                        {!imagesLoaded[slideNumber] && (
                          <div className="image-loader">Загрузка слайда {slideNumber}...</div>
                        )}
                        <img 
                          src={slideImage} 
                          alt={`Слайд ${slideNumber}`}
                          className="slide-image-element"
                          onLoad={() => handleImageLoad(slideNumber)}
                          onError={(e) => {
                            console.error('Ошибка загрузки:', getFullImageUrl(slide.image_url));
                            (e.target as HTMLImageElement).src = '/placeholder.png';
                          }}
                          style={{ 
                            display: imagesLoaded[slideNumber] ? 'block' : 'none',
                            width: '100%',
                            maxHeight: '400px',
                            objectFit: 'contain'
                          }}
                        />
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}        
        <div className="additional-materials">
          <h4>Дополнительные материалы</h4>
          <div className="materials-content">
            <ul>
              <li>Список рекомендуемой литературы</li>
              <li>Полезные ссылки и ресурсы</li>
              <li>Глоссарий терминов</li>
            </ul>
          </div>
        </div>        
        <button 
          onClick={() => setResult(null)}
          className="reset-button"
        >
          Сгенерировать новую презентацию
        </button>
      </div>
    );
  };
  return (
    <div className="presentation-generation-container">
      <h2>Создание профессиональной презентации под идею</h2>      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}      
      {!result ? (
        <form onSubmit={handleSubmit} className="presentation-form">
          <div className="form-group">
            <label htmlFor="presentation_idea">Название идеи *</label>
            <input
              type="text"
              id="presentation_idea"
              name="presentation_idea"
              value={formData.presentation_idea}
              onChange={handleChange}
              placeholder="Название вашей идеи"
              required
            />
          </div>          
          <div className="form-group">
            <label htmlFor="presentation_description">Описание идеи *</label>
            <textarea
              id="presentation_description"
              name="presentation_description"
              value={formData.presentation_description}
              onChange={handleChange}
              placeholder="Подробно опишите вашу идею"
              rows={5}
              required
            />
          </div>          
          {isLoading && (
            <div className="progress-container">
              <div className="progress-bar" style={{ width: `${progress}%` }}></div>
              <p>Генерация презентации: {progress}%</p>
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
                Генерируем презентацию...
              </>
            ) : (
              'Создать презентацию'
            )}
          </button>
        </form>
      ) : (
        renderPresentation()
      )}
      
      <div className="footer-note">
        Советница АКВИ создает профессиональные презентации с использованием передовых моделей искусственного интеллекта и генерации изображений.
        Результаты носят рекомендательный характер и могут быть адаптированы под ваши потребности.
      </div>
    </div>
  );
};

export default PresentationForm;