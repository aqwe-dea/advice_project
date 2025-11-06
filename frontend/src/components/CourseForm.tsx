import React, { useState } from 'react';
import axios from 'axios';
import '../App.css';

const CourseForm = () => {
  const [topic, setTopic] = useState<string>('');
  const [level, setLevel] = useState<string>('начинающий');
  const [courseBook, setCourseBook] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  //const [formData, setFormData] = useState({
    //course_topic: '',
    //target_audience: 'начинающие',
    //course_duration: '4 недели',
    //knowledge_level: 'базовый',
    //course_format: 'онлайн с видеоуроками',
    //learning_objectives: '',
    //practical_tasks: 'есть',
    //certification: 'есть'
  //});
  const [result, setResult] = useState<any>(null);
  const handleGenerateCourse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) {
      setError('Пожалуйста, укажите тему курса');
      return;
    }
    setIsLoading(true);
    setError('');
    setCourseBook('');
    try {
      const structureResponse = await axios.post(
        '/generate-course/',
        { topic, level },
        { headers: { 'Content-Type': 'application/json' } }
      );
      if (structureResponse.data.course_structure) {
        const bookResponse = await axios.post(
          '/generate-course/build_course_book/',
          { 
            course_structure: structureResponse.data.course_structure,
            course_topic: topic 
          },
          { headers: { 'Content-Type': 'application/json' } }
        );
        if (bookResponse.data.course_book) {
          setCourseBook(bookResponse.data.course_book);
        } else {
          setError('Сервер вернул пустой ответ. Попробуйте другую тему.');
        }
      } else {
        setError('Сервер вернул пустую структуру курса.');
      }
    } catch (err: any) {
      console.error('Ошибка запроса:', err);
      if (err.response) {
        setError(`Ошибка ${err.response.status}: ${err.response.data.error || 'Не удалось сгенерировать курс'}`);
      } else if (err.request) {
        setError('Нет ответа от сервера. Проверьте подключение к интернету.');
      } else {
        setError('Произошла ошибка при отправке запроса.');
      }
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
      return text.substring(startIndex).trim();
    }
    return text.substring(startIndex, endIndex).trim();
  };
  const parseCourseBook = (text: string): string => {
    let cleanText = text.trim();
    cleanText = cleanText.replace(/### (.*?)(?=\n|$)/g, '<h4>$1</h4>');
    cleanText = cleanText.replace(/## (.*?)(?=\n|$)/g, '<h3>$1</h3>');
    cleanText = cleanText.replace(/# (.*?)(?=\n|$)/g, '<h2>$1</h2>');
    cleanText = cleanText.replace(/^- (.*?)(?=\n|$)/gm, '<li>$1</li>');
    cleanText = cleanText.replace(/(<li>.*?<\/li>+)/gs, '<ul>$1</ul>');
    cleanText = cleanText.replace(/\n\n/g, '</p><p>');
    cleanText = cleanText.replace(/\n/g, '<br/>');
    if (!cleanText.startsWith('<p>')) {
      cleanText = `<p>${cleanText}`;
    }
    if (!cleanText.endsWith('</p>')) {
      cleanText = `${cleanText}</p>`;
    }
    return cleanText;
  };
  return (
    <div className="course-form">
      <h2>Создать индивидуальный учебник</h2>
      {error && (
        <div className="error-message">{error}</div>
      )}
      <form onSubmit={handleGenerateCourse}>
        <div className="form-group">
          <label htmlFor="topic">Тема курса</label>
          <input
            type="text"
            id="topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="level">Уровень</label>
          <select
            id="level"
            value={level}
            onChange={(e) => setLevel(e.target.value)}
          >
            <option value="начинающий">Начинающий</option>
            <option value="средний">Средний</option>
            <option value="эксперт">Эксперт</option>
          </select>
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Генерируем учебник...' : 'Сгенерировать учебник'}
        </button>
      </form>
      {courseBook && (
        <div className="course-book-result">
        <h3>Ваш учебник:</h3>
        <div className="course-content" dangerouslySetInnerHTML={{__html: parseCourseBook(courseBook)}} />
        </div>
      )}
      <div className="footer-note">
        Советница АКВИ создает структурированные учебники с использованием передовых моделей искусственного интеллекта.
        Результаты носят рекомендательный характер и могут быть адаптированы под ваши потребности.
      </div>
    </div>
  );
};

export default CourseForm;