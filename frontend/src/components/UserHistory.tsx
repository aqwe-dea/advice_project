import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface HistoryItem {
    id: number;
    advice: {
        category: string;
        question: string;
        answer: string;
    };
    created_at: string;
}

function UserHistory({ userId}: { userId: string}) {
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await axios.get<HistoryItem[]>(
                    `https://advice-project.onrender.com/api/user-history/?user_id=${userId}`
                );
                setHistory(response.data);
                setLoading(false);
            } catch (error) {
                console.error('Ошибка при получении истории:', error);
                setLoading(false);
            }
        };
        fetchHistory();
        }, [userId]);
        
        if (loading) {
            return <div>Загрузка...</div>;
        }
        
        return (
            <div>
            <h1>История консультаций</h1>
            <ul>
            {history.map((item) => (
                <li key={item.id}>
                    <strong>{item.advice.category}</strong>: {item.advice.question}
                    <p>Ответ: {item.advice.answer}</p>
                    <small>Дата: {item.created_at}</small>
                </li>
            ))}
            </ul>
            </div>
        )};

export default UserHistory;