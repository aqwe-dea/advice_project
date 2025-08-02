import React, { useState } from 'react';
import axios from 'axios';

const CourseForm = () => {
    const [topic, setTopic] = useState<string>('');
    const [level, setLevel] = useState<string>('начинающий');
    const [course, setCourse] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!topic.trim()) {
            setError('Пожалуйста, укажите тему курса');
            return;
        }
        setIsLoading(true);
        setError('');
        try {
            const response = await axios.post(
                'https://advice-project.onrender.com/generate-course/',
                { topic, level },
                { 
                    headers: { 
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    timeout: 30000 // 30 секунд таймаута
                };
            );
            if (response.data.course_plan) {
            setCourse(response.data.course_plan);
            } else {
                setError('Сервер вернул пустой ответ. Попробуйте другую тему.');
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
    return (
        <div className="course-form">
            <h2>Создать индивидуальный курс</h2>
            {error && (
                <div className="error-message" style={{color: 'red', marginBottom: '1rem'}}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit}>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="topic" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Тема курса
                    </label>
                    <input
                        type="text"
                        id="topic"
                        placeholder="Введите тему курса (например, Python, финансовая грамотность)"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                        disabled={isLoading}
                    />
                </div>
               <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="level" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Уровень подготовки
                    </label>
                    <select 
                        id="level" 
                        value={level} 
                        onChange={(e) => setLevel(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                        disabled={isLoading}
                    >
                        <option value="начинающий">Начинающий</option>
                        <option value="средний">Средний</option>
                        <option value="эксперт">Эксперт</option>
                    </select>
                </div>
                <button 
                    type="submit" 
                    disabled={isLoading}
                    style={{
                        backgroundColor: isLoading ? '#cccccc' : '#007bff',
                        color: 'white',
                        border: 'none',
                        padding: '0.75rem 1.5rem',
                        fontSize: '1rem',
                        cursor: isLoading ? 'not-allowed' : 'pointer'
                    }}
                >
                    {isLoading ? 'Генерация курса...' : 'Создать курс'}
                </button>
            </form>
            {course && (
                <div className="course-result" style={{marginTop: '2rem', border: '1px solid #ddd', padding: '1rem', borderRadius: '4px'}}>
                    <h3 style={{marginTop: '0'}}>Ваш курс:</h3>
                    <div 
                        className="course-content" 
                        style={{
                            whiteSpace: 'pre-wrap',
                            lineHeight: '1.6',
                            fontFamily: 'Arial, sans-serif'
                        }}
                    >
                        {course}
                    </div>
                </div>
            )}
        </div>
    );
};
export default CourseForm;