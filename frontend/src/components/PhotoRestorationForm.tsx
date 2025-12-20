import React, { useState, useRef } from 'react';
import '../App.css';

const PhotoRestorationForm = () => {
  const [image, setImage] = useState<File | null>(null);
  const [restorationInfo, setRestorationInfo] = useState({
    damage_type: 'потертости и царапины',
    damage_level: 'средняя',
    restoration_style: 'оригинальный стиль',
    special_requests: '',
    photo_age: 'неизвестно'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [progress, setProgress] = useState(0);
  const imageInputRef = useRef<HTMLInputElement>(null);
  
  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedImage = e.target.files[0];
      const allowedExtensions = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp'];
      const fileExt = selectedImage.name.toLowerCase().split('.').pop();
      if (!fileExt || !allowedExtensions.includes(`.${fileExt}`)) {
        setError(`Поддерживаются только форматы: ${allowedExtensions.join(', ')}`);
        if (imageInputRef.current) {
          imageInputRef.current.value = '';
        }
        return;
      }
      setImage(selectedImage);
      setError(null);
    }
  };
  
  const handleRestorationInfoChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setRestorationInfo(prev => ({ ...prev, [name]: value }));
  };
  
  const handleRestore = async () => {
    if (!image) {
      setError('Пожалуйста, загрузите фотографию');
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
          return prev + 5;
        });
      }, 300);
      
      const formData = new FormData();
      formData.append('image', image);
      formData.append('damage_type', restorationInfo.damage_type);
      formData.append('damage_level', restorationInfo.damage_level);
      formData.append('restoration_style', restorationInfo.restoration_style);
      formData.append('special_requests', restorationInfo.special_requests);
      formData.append('photo_age', restorationInfo.photo_age);
      
      const response = await fetch('/photo-restoration/', {
        method: 'POST',
        body: formData
      });
      
      clearInterval(progressInterval);
      setProgress(100);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Ошибка при реставрации фотографии');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка при реставрации фотографии');
    } finally {
      setIsLoading(false);
    }
  };
  
  const renderRestorationPlan = () => {
    if (!result || !result.restoration_report) return null;
    
    const report = result.restoration_report;
    
    return (
      <div className="restoration-plan">
        <h3>Результаты реставрации фотографии: {result.image_type}</h3>
        
        <div className="comparison-container">
          <div className="before">
            <h4>До реставрации</h4>
            <img src={report.before_after_comparison.original_url} alt="Оригинал" className="comparison-image" />
          </div>
          <div className="after">
            <h4>После реставрации</h4>
            <img src={report.before_after_comparison.restored_url} alt="Восстановленное" className="comparison-image" />
          </div>
        </div>
        
        <div className="section">
          <h4>Анализ повреждений</h4>
          <div className="section-content">
            <p>Тип повреждений: {report.restoration_summary.damage_type}</p>
            <p>Степень повреждения: {report.restoration_summary.damage_level}</p>
            <p>Возраст фотографии: {report.restoration_summary.photo_age}</p>
          </div>
        </div>
        
        <div className="section">
          <h4>Рекомендации по уходу</h4>
          <div className="section-content">
            <p>Хранение: {report.recommendations.storage}</p>
            <p>Обращение: {report.recommendations.handling}</p>
            <p>Долгосрочный уход: {report.recommendations.long_term_care}</p>
          </div>
        </div>
        
        <button 
          onClick={() => setResult(null)}
          className="reset-button"
        >
          Запланировать новую реставрацию
        </button>
      </div>
    );
  };
  
  return (
    <div className="restoration-container">
      <h2>Реставрация фотографий</h2>
      <p>Загрузите поврежденную фотографию для профессионального анализа и планирования реставрации</p>
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      <div className="form-section">
        <div className="form-group">
          <label htmlFor="image">Фотография *</label>
          <input
            type="file"
            id="image"
            accept=".jpg,.jpeg,.png,.tiff,.bmp"
            onChange={handleImageChange}
            ref={imageInputRef}
            disabled={isLoading}
          />
          {image && (
            <div className="file-info">
              <span>Выбрано изображение: {image.name}</span>
              <button 
                onClick={() => {
                  setImage(null);
                  if (imageInputRef.current) {
                    imageInputRef.current.value = '';
                  }
                }}
                disabled={isLoading}
                className="remove-file-button"
              >
                Удалить
              </button>
            </div>
          )}
        </div>
        <div className="form-group">
          <label htmlFor="damage_type">Тип повреждений</label>
          <input
            type="text"
            id="damage_type"
            name="damage_type"
            value={restorationInfo.damage_type}
            onChange={handleRestorationInfoChange}
            placeholder="Например: потертости, царапины, пятна, выцветание"
            disabled={isLoading}
          />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="damage_level">Степень повреждения</label>
            <select
              id="damage_level"
              name="damage_level"
              value={restorationInfo.damage_level}
              onChange={handleRestorationInfoChange}
              disabled={isLoading}
            >
              <option value="незначительная">Незначительная</option>
              <option value="средняя">Средняя</option>
              <option value="серьезная">Серьезная</option>
              <option value="критическая">Критическая</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="photo_age">Возраст фотографии</label>
            <input
              type="text"
              id="photo_age"
              name="photo_age"
              value={restorationInfo.photo_age}
              onChange={handleRestorationInfoChange}
              placeholder="Например: 1950-е годы"
              disabled={isLoading}
            />
          </div>
        </div>
        <div className="form-group">
          <label htmlFor="restoration_style">Стиль реставрации</label>
          <select
            id="restoration_style"
            name="restoration_style"
            value={restorationInfo.restoration_style}
            onChange={handleRestorationInfoChange}
            disabled={isLoading}
          >
            <option value="оригинальный стиль">Оригинальный стиль</option>
            <option value="современная интерпретация">Современная интерпретация</option>
            <option value="минималистичный">Минималистичный</option>
            <option value="художественная реставрация">Художественная реставрация</option>
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="special_requests">Специальные пожелания</label>
          <textarea
            id="special_requests"
            name="special_requests"
            value={restorationInfo.special_requests}
            onChange={handleRestorationInfoChange}
            placeholder="Укажите особые требования к реставрации"
            rows={3}
            disabled={isLoading}
          />
        </div>
      </div>
      {isLoading && (
        <div className="progress-section">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p className="progress-text">
            {progress < 30 ? 'Анализируем фотографию...' : 
             progress < 60 ? 'Определяем тип повреждений...' :
             progress < 90 ? 'Формируем план реставрации...' : 'Готовим рекомендации...'}
          </p>
        </div>
      )}
      {result ? (
        renderRestorationPlan()
      ) : (
        <button 
          onClick={handleRestore} 
          disabled={isLoading || !image}
          className="restore-button"
        >
          {isLoading ? (
            <>
              <span className="spinner"></span>
              Планируем реставрацию...
            </>
          ) : (
            'Запланировать реставрацию'
          )}
        </button>
      )}
      <div className="footer-note">
        Советница АКВИ анализирует состояние фотографий и планирует реставрацию с использованием передовых моделей искусственного интеллекта. 
        Результаты носят рекомендательный характер и могут быть адаптированы под ваши потребности.
      </div>
    </div>
  );
};

export default PhotoRestorationForm;