import React, { useEffect, useState } from 'react';
import axios from 'axios';
import '../styles/AdviceList.css';
//import SearchBar from './SearchBar';
import AdviceCard from './AdviceCard';
import Spoiler from './Spoiler';

interface Advice {
    id: number;
    category: string;
    question: string;
    answer: string;
    created_at: string;
}

function AdviceList() {
    const [advices, setAdvices] = useState<Advice[]>([]);
    //const [searchTerm, setSearchTerm] = useState('');
    const [loading, setLoading] = useState(true)

     useEffect(() => {
        const fetchAdvices = async () => {
            try {
                const response = await axios.get<Advice[]>(
                    'http://127.0.0.1:8000/api/advice/'
                );
                setAdvices(response.data);
                setLoading(false);
            } catch (error) {
                console.error('Ошибка при получении данных:', error);
                setLoading(false);
            }
        };
        fetchAdvices();
     }, []);
if (loading) {
        return <div>Загрузка...</div>;
       }
    const [selectedCategory, setSelectedCategory] = useState('')
    const filteredAdvices = advices.filter((advice) =>  
        !selectedCategory || advice.category === selectedCategory,
    //advice.question.toLowerCase().includes(searchTerm.toLowerCase())
    
    )
    //<SearchBar onSearch={setSearchTerm} />
        return (
        <div>
            <h1>Список консультаций</h1>
            <ul>
             {advices.map((advice) =>(
                    <li key={advice.id}>
                        <a href={`/advice/${advice.id}`}>
                        <strong>{advice.category}</strong>: {advice.question}
                        </a>

                        <Spoiler title={advice.category} content={advice.question} />
                    </li>
                ))}
                {filteredAdvices.map(advice => (
                <AdviceCard key={advice.id} advice={advice} />   
             ))}
            <select 
            value={selectedCategory} 
            onChange={(e) => setSelectedCategory(e.target.value)}>
            <option value="">Все категории</option>
            <option value="финансы">Финансы</option>
            <option value="здоровье">Здоровье</option>
            <option value="образование">Образование</option>
            
            </select>
            </ul>
        </div>
     )
}

export default AdviceList;