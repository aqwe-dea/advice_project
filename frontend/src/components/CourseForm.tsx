import React, { useState } from 'react';

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
            const response = await fetch(
                `https://advice-project.onrender.com/generate-course/?age=${age}&interests=${encodeURIComponent(interests)}&level=${level}`,
                { method: "GET" }
            );
            if (!response.ok) {
                throw new Error(`Ошибка сети: ${response.status} ${response.statusText}`);
            }
            const data = await response.json();
            if (data.text) {
                setCourse(data.text);
            } else if (data.error) {
                setError(data.error);
            } else {
                setError("Неожиданный формат ответа");
            }
        } catch (err: any) {
            setError(err.message || "Произошла ошибка");
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