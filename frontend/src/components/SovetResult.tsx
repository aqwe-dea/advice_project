import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

interface SovetResultProps {};

function SovetResult({}: SovetResultProps) {
    const [advice, setAdvice] = useState<{ id: string; category: string; question: string; answer: string; notes?: string; } | null>(
        null
    );
    const { id }: { id: string | undefined; } = useParams();
    useEffect(() => {
        if (!id) return;
        const fetchAdvice = async () => {
            try {
                const response = await axios.get(
                    'https://advice-project.onrender.com/api/advice/${id}/'
                );
                setAdvice(response.data);
            } catch (error) {
                console.error('Ошибка при загрузке совета:', error);
                alert('Не удалось загрузить совет.');
            }
        };
        fetchAdvice();
    }, [id]);
    if (!advice) return <div>Загрузка...</div>; 
    return (
        <div className="sovet-result">
            <h1>Ваш детальный совет:</h1>
            <p><strong>Категория:</strong> {advice.category}</p>
            <p><strong>Вопрос:</strong> {advice.question}</p>
            <p><strong>Ответ:</strong> {advice.answer}</p>
            <p><strong>Заметки:</strong> {advice.notes || 'Нет заметок'}</p>
            </div>
            );
}

export default SovetResult;