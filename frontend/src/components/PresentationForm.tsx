import React, { useState, useRef } from 'react';
import '../App.css';

const PresentationForm = () => {
  const [formData, setFormData] = useState({
    topic: '',
    audience: 'широкая аудитория',
    duration: '15-20 минут',
    purpose: 'информирование',
    style: 'профессиональный',
    slides_count: '15-20'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [progress, setProgress] = useState(0);
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.topic.trim()) {
      setError('Пожалуйста, укажите тему презентации');
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
    const sections = {
      title: extractSection(result.presentation, "# НАЗВАНИЕ ПРЕЗЕНТАЦИИ", "## 1."),
      introduction: extractSection(result.presentation, "## 1. ВВЕДЕНИЕ", "## 2."),
      main: extractSection(result.presentation, "## 2. ОСНОВНАЯ ЧАСТЬ", "## 3."),
      conclusions: extractSection(result.presentation, "## 3. КЛЮЧЕВЫЕ ВЫВОДЫ", "## 4."),
      faq: extractSection(result.presentation, "## 4. ЧАСТЫЕ ВОПРОСЫ И ОТВЕТЫ", "## 5."),
      conclusion: extractSection(result.presentation, "## 5. ЗАКЛЮЧЕНИЕ", "## 6."),
      additional: extractSection(result.presentation, "## 6. ДОПОЛНИТЕЛЬНЫЕ МАТЕРИАЛЫ", "## 7."),
      recommendations: extractSection(result.presentation, "## 7. РЕКОМЕНДАЦИИ ПО ПОДГОТОВКЕ", null)
    };
    return (
      <div className="presentation">
        <h3>Презентация: {formData.topic}</h3>
        <div className="section">
          <h4>Название презентации</h4>
          <div className="section-content">{sections.title || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>1. Введение</h4>
          <div className="section-content">{sections.introduction || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>2. Основная часть</h4>
          <div className="section-content">{sections.main || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>3. Ключевые выводы</h4>
          <div className="section-content">{sections.conclusions || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>4. Частые вопросы и ответы</h4>
          <div className="section-content">{sections.faq || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>5. Заключение</h4>
          <div className="section-content">{sections.conclusion || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>6. Дополнительные материалы</h4>
          <div className="section-content">{sections.additional || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>7. Рекомендации по подготовке</h4>
          <div className="section-content">{sections.recommendations || "Не найдено"}</div>
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
    <div className="presentation-container">
      <h2>Генерация презентации</h2>
      <p>Заполните форму для создания структурированной презентации</p>
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      {!result ? (
        <form onSubmit={handleSubmit} className="presentation-form">
          <div className="form-group">
            <label htmlFor="topic">Тема презентации *</label>
            <textarea
              id="topic"
              name="topic"
              value={formData.topic}
              onChange={handleChange}
              placeholder="Опишите тему вашей презентации"
              rows={3}
              required
            />
          </div>  
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="audience">Целевая аудитория</label>
              <input
                type="text"
                id="audience"
                name="audience"
                value={formData.audience}
                onChange={handleChange}
                placeholder="Например: руководители, студенты, инвесторы"
              />
            </div>
            <div className="form-group">
              <label htmlFor="duration">Продолжительность</label>
              <input
                type="text"
                id="duration"
                name="duration"
                value={formData.duration}
                onChange={handleChange}
                placeholder="Например: 15-20 минут"
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="purpose">Цель презентации</label>
              <select
                id="purpose"
                name="purpose"
                value={formData.purpose}
                onChange={handleChange}
              >
                <option value="информирование">Информирование</option>
                <option value="убеждение">Убеждение</option>
                <option value="обучение">Обучение</option>
                <option value="мотивация">Мотивация</option>
                <option value="продажа">Продажа</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="slides_count">Количество слайдов</label>
              <input
                type="text"
                id="slides_count"
                name="slides_count"
                value={formData.slides_count}
                onChange={handleChange}
                placeholder="Например: 15-20"
              />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="style">Стиль презентации</label>
            <select
              id="style"
              name="style"
              value={formData.style}
              onChange={handleChange}
            >
              <option value="профессиональный">Профессиональный</option>
              <option value="креативный">Креативный</option>
              <option value="минималистичный">Минималистичный</option>
              <option value="информационный">Информационный</option>
              <option value="сторителлинг">Сторителлинг</option>
            </select>
          </div>
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
              'Сгенерировать презентацию'
            )}
          </button>
        </form>
      ) : (
        renderPresentation()
      )}
      <div className="footer-note">
        Советница АКВИ создает структурированные презентации с использованием передовых моделей искусственного интеллекта. 
        Результаты носят рекомендательный характер и могут быть адаптированы под ваши потребности.
      </div>
    </div>
  );
};

export default PresentationForm;