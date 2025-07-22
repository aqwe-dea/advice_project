import React, { useState } from 'react';
import axios from 'axios';

const CourseForm = () => {
    const [course, setCourse] = useState<string>("");
    const [topic, setTopic] = useState<string>('');
    const [level, setLevel] = useState<string>('начинающий');
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!topic.trim()) return;
        try {
            const response = await axios.post(
                'https://advice-project.onrender.com/generate-course/ ',
                { topic, level },
                { headers: { 'Content-Type': 'application/json' } }
            );
            console.log('Ответ от сервера:', response.data);
            setCourse(response.data.course_plan || 'Не удалось сгенерировать курс');
        } catch (error: any) {
            console.error('Ошибка:', {
                status: error.response?.status,
                message: error.message
            });
            alert('Не удалось сгенерировать курс. Проверьте тему и уровень.');
        }
    };
    return (
        <div className="course-form">
            <h2>Создать индивидуальный курс</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Тема курса"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                />
                <select value={level} onChange={(e) => setLevel(e.target.value)}>
                    <option value="начинающий">Начинающий</option>
                    <option value="средний">Средний</option>
                    <option value="эксперт">Эксперт</option>
                </select>
                <button type="submit">Создать курс</button>
            </form>
            {course && <div className="course-result"><p>{course}</p></div>}
        </div>
    );
};
export default CourseForm;