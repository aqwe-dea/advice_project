import React, { useState, useEffect } from 'react';
import axios from 'axios';

//interface Advice {
//     id: number;
//     name: string;
//     email: string;
//     category: string;
//     question: string;
//     answer: string;
//     notes: string;
//}

interface SovetResultProps {}

function SovetResult({ id }: SovetResultProps) {
    const [advice, setAdvice] = useState<any | null>(null);
    const {id} = useParams();
    useEffect(() => {
        const fetchAdvice = async () => {
            if (!id) return;
            try {
                const response = await axios.get(
                    `https://advice-project.onrender.com/api/advice/${id}/`
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
            <p><strong>Заметки:</strong> {advice.notes}</p>
        </div>
    );
}

export default SovetResult;