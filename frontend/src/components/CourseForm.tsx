import React, { useState } from 'react';

const CourseFprm = () => {
    const [course, setCourse] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const handleSubmit = async (e:React.FormEvent) => {
        e.prevent.Default();
        setIsLoading(true);
        const formData = new FormData(e.currentTarget);
        const age = formData.get("age") as string;
        const interests = formData.get("interests") as string;
        const level = formData.get("level") as string;
        try {
            const response = await fetch(
                `https://advice-project.onrender.com/generate-course/?age=${age}&interests=${encodeURIComponent(interests)}&level=${level}`,
                { method: "GET" }
            );
            const data = await response.json();
            setCourse(data[0]?.generated_text || JSON.stringify(data));
        } catch (error) {
            setCourse("Ошибка генерации курса");
        } finally {
            setIsLoading(false);
        }
    };
    return (
        <form onSubmit={handleSubmit}>
            <h3>Создать индивидуальный курс</h3>
            <label>
                Возраст:
                <input name="age" type="number" defaultValue="25" required />
            </label>
            <label>
                Интересы (через запятую):
                <input name="interests" placeholder="Программирование, дизайн..." required />
            </label>
            <label>
                Уровень:
                <select name="level">
                    <option value="новичок">Новичок</option>
                    <option value="средний">Средний</option>
                    <option value="опытный">Опытный</option>
                </select>
            </label>
            <button type="submit" disable={isLoading}>
                {isLoading ? "Генерация..." : "Создать курс"}
            </button>
            <pre>{course}</pre>
        </form>
    );
};

export default CourseForm;