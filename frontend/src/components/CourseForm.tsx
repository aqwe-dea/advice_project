import React, { useState } from 'react';
import axios from 'axios';

const CourseForm = () => {
    const [course, setCourse] = useState<string>("");
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>("");
    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setIsLoading(true);
        setError("");
        const form = e.currentTarget as HTMLFormElement;
        const formData = new FormData(form);
        const age = formData.get("age") as string;
        const interests = formData.get("interests") as string;
        const level = formData.get("level") as string;
        try {
            const response = await axios.get(
                `https://advice-project.onrender.com/generate-course/?age=${age}&interests=${encodeURIComponent(interests)}&level=${level}`
            );
            if (response.data.text) {
                setCourse(response.data.text);
            } else {
                setError("Не удалось получить курс");
            }
        } catch (err: any) {
            setError(`Ошибка сети: $(err.message)`);
            console.error("Ошибка:", err.response?.data || err);
        } finally {
            setIsLoading(false);
        }
    };
    return (
        <div style={{ padding: "20px" }}>
            <h2>Создать индивидуальный курс</h2>
            <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                <label>
                    Возраст:
                    <input name="age" type="number" defaultValue="25" required style={{ marginLeft: "10px" }} />
                </label>
                <label>
                    Интересы (через запятую):
                    <input name="interests" placeholder="Программирование, дизайн..." required style={{ marginLeft: "10px" }} />
                </label>
                <label>
                    Уровень:
                    <select name="level" style={{ marginLeft: "10px" }}>
                        <option value="новичок">Новичок</option>
                        <option value="средний">Средний</option>
                        <option value="опытный">Опытный</option>
                    </select>
                </label>
                <button type="submit" disabled={isLoading} style={{ width: "200px" }}>
                    {isLoading ? "Генерация..." : "Создать курс"}
                </button>
            </form>
        {course && (
            <pre style={{ marginTop: "10px", whiteSpace: "pre_wrap" }}>{course}</pre>
        )}
        {error && (
            <div style={{ color: "red", marginTop: "20px" }}>{error}</div>
        )}
        {isLoading && (
            <div style={{ marginTop: "20px" }}>Подождите, генерация курса...</div>
        )}
    </div>
);
};
export default CourseForm;