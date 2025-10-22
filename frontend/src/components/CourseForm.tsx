import React, { useState } from 'react';
import '../App.css';

const CourseForm = () => {
  const [formData, setFormData] = useState({
    course_topic: '',
    target_audience: 'начинающие',
    course_duration: '4 недели',
    knowledge_level: 'базовый',
    course_format: 'онлайн с видеоуроками',
    learning_objectives: '',
    practical_tasks: 'есть',
    certification: 'есть'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.course_topic.trim()) {
      setError('Пожалуйста, укажите тему курса');
      return;
    }
    if (!formData.learning_objectives.trim()) {
      setError('Пожалуйста, укажите цели обучения');
      return;
    }
    setIsLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch('/generate-course/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Ошибка при генерации курса');
      }
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка при генерации курса');
    } finally {
      setIsLoading(false);
    }
  };
  const renderCourseStructure = () => {
    if (!result || !result.course_structure) return null;
    const sections = {
      introduction: extractSection(result.course_structure, "1.", "2."),
      modules: extractSection(result.course_structure, "2.", "3."),
      methodology: extractSection(result.course_structure, "3.", "4."),
      practical: extractSection(result.course_structure, "4.", "5."),
      assessment: extractSection(result.course_structure, "5.", "6."),
      materials: extractSection(result.course_structure, "6.", "7."),
      schedule: extractSection(result.course_structure, "7.", "8."),
      caseStudies: extractSection(result.course_structure, "8.", "9."),
      support: extractSection(result.course_structure, "9.", "10."),
      recommendations: extractSection(result.course_structure, "10.", null)
    };
    return (
      <div className="course-structure">
        <h3>Структура курса: {result.course_topic}</h3>
        <div className="section">
          <h4>1. Введение в курс</h4>
          <div className="section-content">{sections.introduction || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>2. Подробная структура курса (по модулям)</h4>
          <div className="section-content">{sections.modules || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>3. Методология обучения</h4>
          <div className="section-content">{sections.methodology || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>4. Практические задания и проекты</h4>
          <div className="section-content">{sections.practical || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>5. Оценка знаний и обратная связь</h4>
          <div className="section-content">{sections.assessment || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>6. Рекомендуемые материалы</h4>
          <div className="section-content">{sections.materials || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>7. Расписание и план занятий</h4>
          <div className="section-content">{sections.schedule || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>8. Примеры успешных кейсов</h4>
          <div className="section-content">{sections.caseStudies || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>9. Поддержка студентов</h4>
          <div className="section-content">{sections.support || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>10. Рекомендации по дальнейшему обучению</h4>
          <div className="section-content">{sections.recommendations || "Не найдено"}</div>
        </div>
        <button 
          onClick={() => setResult(null)}
          className="reset-button"
        >
          Сгенерировать новый курс
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
    <div className="course-generation-container">
      <h2>Генерация образовательного курса</h2>
      <p>Заполните форму для создания структуры образовательного курса</p>
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      {!result ? (
        <form onSubmit={handleSubmit} className="course-form">
          <div className="form-group">
            <label htmlFor="course_topic">Тема курса *</label>
            <input
              type="text"
              id="course_topic"
              name="course_topic"
              value={formData.course_topic}
              onChange={handleChange}
              placeholder="Например: Основы программирования на Python"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="target_audience">Целевая аудитория</label>
            <select
              id="target_audience"
              name="target_audience"
              value={formData.target_audience}
              onChange={handleChange}
            >
              <option value="начинающие">Начинающие</option>
              <option value="средний уровень">Средний уровень</option>
              <option value="продвинутый уровень">Продвинутый уровень</option>
              <option value="специалисты">Специалисты</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="course_duration">Продолжительность курса</label>
            <input
              type="text"
              id="course_duration"
              name="course_duration"
              value={formData.course_duration}
              onChange={handleChange}
              placeholder="Например: 4 недели, 8 недель, 3 месяца"
            />
          </div>
          <div className="form-group">
            <label htmlFor="knowledge_level">Уровень знаний</label>
            <select
              id="knowledge_level"
              name="knowledge_level"
              value={formData.knowledge_level}
              onChange={handleChange}
            >
              <option value="базовый">Базовый</option>
              <option value="средний">Средний</option>
              <option value="углубленный">Углубленный</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="course_format">Формат курса</label>
            <input
              type="text"
              id="course_format"
              name="course_format"
              value={formData.course_format}
              onChange={handleChange}
              placeholder="Например: онлайн с видеоуроками, очные занятия, гибридный формат"
            />
          </div>
          <div className="form-group">
            <label htmlFor="learning_objectives">Цели обучения *</label>
            <textarea
              id="learning_objectives"
              name="learning_objectives"
              value={formData.learning_objectives}
              onChange={handleChange}
              placeholder="Опишите, что студенты должны знать и уметь после прохождения курса"
              rows={4}
              required
            />
          </div>
          <div className="form-group">
            <label>Практические задания</label>
            <div className="radio-group">
              <label>
                <input
                  type="radio"
                  name="practical_tasks"
                  value="есть"
                  checked={formData.practical_tasks === 'есть'}
                  onChange={handleChange}
                />
                Есть
              </label>
              <label>
                <input
                  type="radio"
                  name="practical_tasks"
                  value="нет"
                  checked={formData.practical_tasks === 'нет'}
                  onChange={handleChange}
                />
                Нет
              </label>
            </div>
          </div>
          <div className="form-group">
            <label>Сертификация</label>
            <div className="radio-group">
              <label>
                <input
                  type="radio"
                  name="certification"
                  value="есть"
                  checked={formData.certification === 'есть'}
                  onChange={handleChange}
                />
                Есть
              </label>
              <label>
                <input
                  type="radio"
                  name="certification"
                  value="нет"
                  checked={formData.certification === 'нет'}
                  onChange={handleChange}
                />
                Нет
              </label>
            </div>
          </div>
          <button 
            type="submit" 
            className="generate-button"
            disabled={isLoading}
          >
            {isLoading ? 'Генерируем курс...' : 'Сгенерировать курс'}
          </button>
        </form>
      ) : (
        renderCourseStructure()
      )}
      <div className="footer-note">
        Советница АКВИ создает структуру образовательных курсов с использованием передовых моделей искусственного интеллекта. 
        Результаты носят рекомендательный характер и могут быть адаптированы под ваши потребности.
      </div>
    </div>
  );
};

export default CourseForm;