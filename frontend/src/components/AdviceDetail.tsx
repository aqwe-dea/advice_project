import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Advice {
    id: number;
    category: string;
    question: string;
    answer: string;
    created_at: string;
}

function AdviceDetail({ adviceId }: {adviceId: number}) {
    const [advice, setAdvice] = useState<Advice | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAdvice = async () => {
            try {
                const response = await axios.get<Advice>(
                    `http://127.0.0.1:8000/api/advice/${adviceId}/`
                );
                setAdvice(response.data);
                setLoading(false);
            } catch (error) {
                console.error('Ошибка при получении консультации:', error);
                setLoading(false);
            }
            
        };
        fetchAdvice();
    }, [adviceId]);
if (loading) {
    return <div>Загрузка...</div>;
}
if (!advice) {
    return <div>Консультация не найдена</div>;
}
return (
    <div>
        <h1>Детальная информация</h1>
        <p><strong>Категория:</strong> {advice.category}</p>
        <p><strong>Вопрос:</strong> {advice.question}</p>
        <p><strong>Ответ:</strong> {advice.answer}</p>
        <p><strong>Дата создания:</strong> {advice.created_at}</p>
    </div>
);
}

export default AdviceDetail;