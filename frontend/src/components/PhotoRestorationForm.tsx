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
    if (!result || !result.restoration_plan) return null;
    const sections = {
      analysis: extractSection(result.restoration_plan, "1.", "2."),
      methods: extractSection(result.restoration_plan, "2.", "3."),
      expected: extractSection(result.restoration_plan, "3.", "4."),
      preservation: extractSection(result.restoration_plan, "4.", "5."),
      additional: extractSection(result.restoration_plan, "5.", "6."),
      timeline: extractSection(result.restoration_plan, "6.", "7."),
      care: extractSection(result.restoration_plan, "7.", null)
    };
    return (
      <div className="restoration-plan">
        <h3>План реставрации фотографии: {result.image_type}</h3>
        <div className="section">
          <h4>1. Анализ состояния фотографии</h4>
          <div className="section-content">{sections.analysis || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>2. Методы реставрации</h4>
          <div className="section-content">{sections.methods || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>3. Ожидаемый результат</h4>
          <div className="section-content">{sections.expected || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>4. Рекомендации по сохранению</h4>
          <div className="section-content">{sections.preservation || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>5. Дополнительные услуги</h4>
          <div className="section-content">{sections.additional || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>6. Сроки и стоимость</h4>
          <div className="section-content">{sections.timeline || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>7. Советы по дальнейшему уходу</h4>
          <div className="section-content">{sections.care || "Не найдено"}</div>
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