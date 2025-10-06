import React, { useState, useRef } from 'react';
import '../App.css';

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
      const response = await fetch('/3d-to-project/', {
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
  const renderModelingPlan = () => {
    if (!result || !result.modeling_plan) return null;
    const sections = {
      preparation: extractSection(result.modeling_plan, "1.", "2."),
      modeling: extractSection(result.modeling_plan, "2.", "3."),
      texturing: extractSection(result.modeling_plan, "3.", "4."),
      rigging: extractSection(result.modeling_plan, "4.", "5."),
      lighting: extractSection(result.modeling_plan, "5.", "6."),
      postprocessing: extractSection(result.modeling_plan, "6.", "7."),
      export: extractSection(result.modeling_plan, "7.", "8."),
      recommendations: extractSection(result.modeling_plan, "8.", null)
    };
    return (
      <div className="modeling-plan">
        <h3>План 3D-моделирования: {formData.model_type}</h3>
        <div className="section">
          <h4>1. Подготовительный этап</h4>
          <div className="section-content">{sections.preparation || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>2. Этап моделирования</h4>
          <div className="section-content">{sections.modeling || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>3. Текстурирование и материалы</h4>
          <div className="section-content">{sections.texturing || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>4. Риггинг и анимация</h4>
          <div className="section-content">{sections.rigging || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>5. Освещение и рендеринг</h4>
          <div className="section-content">{sections.lighting || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>6. Пост-обработка</h4>
          <div className="section-content">{sections.postprocessing || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>7. Экспорт и интеграция</h4>
          <div className="section-content">{sections.export || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>8. Рекомендации по улучшению</h4>
          <div className="section-content">{sections.recommendations || "Не найдено"}</div>
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