import React, { useState } from 'react';
import '../App.css';

const PresentationForm = () => {
  const [formData, setFormData] = useState({
    presentation_idea: '',
    presentation_description: ''
  });  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [progress, setProgress] = useState(0);
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
      }, 200);      
      const response = await fetch('https://advice-project.onrender.com/generate-presentation/', {
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
  const renderPresentation = () => {
    if (!result || !result.presentation) return null;        
    const slides = result.presentation.split(/##\s+\d+\.\s+/).slice(1);    
    return (
      <div className="presentation-container">
        <h3>Ваша презентация: {result.presentation_idea}</h3>        
        {slides.map((slideContent: string, index: number) => {
          const slideNumber = index + 1;
          const slideTitleMatch = slideContent.match(/^(.+?)\n/);
          const slideTitle = slideTitleMatch ? slideTitleMatch[1].trim() : `Слайд ${slideNumber}`;
          const slideBody = slideContent.replace(/^(.+?)\n/, '').trim();          
          const slideImage = result.images.find((img: any) => img.slide_number === slideNumber);          
          return (
            <div key={slideNumber} className="slide">
              <div className="slide-header">
                <h4>{slideNumber}. {slideTitle}</h4>
              </div>
              <div className="slide-content">
                {slideImage && (
                  <div className="slide-image">
                    <img src={slideImage.image_url} alt={`Слайд ${slideNumber}`} />
                  </div>
                )}
                <div className="slide-text" dangerouslySetInnerHTML={{__html: slideBody.replace(/\n/g, '<br/>')}} />
              </div>
            </div>
          );
        })}        
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