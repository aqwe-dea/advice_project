import React, { useEffect, useState } from "react";
import axios from "axios";
import Spoiler from "./Spoiler";

interface Advice {
    id: number;
    category: string;
    question: string;
    answer: string;
    created_at: string;
}

function AdviceList() {
    const [advices, setAdvices] = useState<Advice[]>([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('');

    useEffect(() => {
        const fetchAdvices = async () => {
            try {
                const response = await axios.get<Advice[]>(
                    'https://advice-project.onrender.com/api/advice/'
                );
                setAdvices(response.data);
            } catch (error) {
                console.error('Ошибка при загрузке данных:', error);
            }
        };

        fetchAdvices();
    }, []);
    const filteredAdvices = advices
     .filter(advice =>
        advice.question.toLowerCase().includes(searchTerm.toLowerCase())
     )
     .filter(advice =>
        !selectedCategory || advice.category === selectedCategory
     );
    
    return (
        <div className="advice-list">
            <input
             type="text"
             placeholder="Поиск по вопросам..."
             value={searchTerm}
             onChange={(e) => setSearchTerm(e.target.value)}
            />
            <select
             value={selectedCategory}
             onChange={(e) => setSelectedCategory(e.target.value)}
             >
                <option value="">Все категории</option>
                <option value="финансы">Финансы</option>
                <option value="здоровье">Здоровье</option>
                <option value="образование">Образование</option>
            </select>

            <ul>
                {filteredAdvices.map(advice => (
                    <li key={advice.id}>
                        <Spoiler
                         title={`${advice.category}: ${advice.question}`}
                         content={advice.answer}
                        />
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default AdviceList;