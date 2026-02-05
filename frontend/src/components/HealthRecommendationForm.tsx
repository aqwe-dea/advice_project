import React, { useState } from 'react';
import '../App.css';
import { styled } from 'styled-components';
import { colors } from '../theme';
import axios from 'axios';

function HealthRecommendationForm() {
    const [symptoms, setSymptoms] = useState<string>('');
    const [age, setAge] = useState<string>('');
    const [gender, setGender] = useState<string>('не указан');
    const [country, setCountry] = useState<string>('Россия');
    const [recommendationType, setRecommendationType] = useState<string>('общие');
    const [recommendation, setRecommendation] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!symptoms.trim()) {
            setError('Пожалуйста, укажите симптомы');
            return;
        }
        setIsLoading(true);
        setError('');
        try {
            const response = await axios.post(
                'https://advice-project.onrender.com/health-recommendation/',
                { 
                    symptoms, 
                    age, 
                    gender, 
                    country,
                    type: recommendationType
                },
                { 
                    headers: { 'Content-Type': 'application/json' },
                    timeout: 30000
                }
            );
            setRecommendation(response.data);
        } catch (err: any) {
            console.error('Ошибка генерации рекомендаций по здоровью:', err);
            if (err.response) {
                setError(`Ошибка ${err.response.status}: ${err.response.data.error || 'Не удалось получить рекомендации'}`);
            } else if (err.request) {
                setError('Нет ответа от сервера. Проверьте подключение к интернету.');
            } else {
                setError('Произошла ошибка при отправке запроса.');
            }
        } finally {
            setIsLoading(false);
        }
    };
    return (
        <div className="health-recommendation-form">
            <h2>Персональные рекомендации по здоровью</h2>
            <p className="disclaimer" style={{color: '#dc3545', fontStyle: 'italic', marginBottom: '1rem'}}>
                Внимание: Эти рекомендации не заменяют профессиональную медицинскую консультацию. 
                Перед применением рекомендаций проконсультируйтесь с врачом.
            </p>
            {error && (
                <div className="error-message" style={{color: 'red', marginBottom: '1rem'}}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit}>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="symptoms" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Опишите ваши симптомы
                    </label>
                    <textarea
                        id="symptoms"
                        placeholder="Опишите ваши симптомы подробно"
                        value={symptoms}
                        onChange={(e) => setSymptoms(e.target.value)}
                        style={{width: '100%', height: '150px', padding: '0.5rem', fontSize: '1rem'}}
                    />
                </div>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="age" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Возраст
                    </label>
                    <input
                        type="number"
                        id="age"
                        placeholder="Ваш возраст"
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    />
                </div>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="gender" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Пол
                    </label>
                    <select 
                        id="gender" 
                        value={gender} 
                        onChange={(e) => setGender(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    >
                        <option value="не указан">Не указан</option>
                        <option value="мужской">Мужской</option>
                        <option value="женский">Женский</option>
                    </select>
                </div>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="recommendation-type" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Тип рекомендаций
                    </label>
                    <select 
                        id="recommendation-type" 
                        value={recommendationType} 
                        onChange={(e) => setRecommendationType(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    >
                        <option value="общие">Общие рекомендации</option>
                        <option value="натуральные">Натуральные средства</option>
                        <option value="древние">Древние методы</option>
                        <option value="питание">Рекомендации по питанию</option>
                    </select>
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="country" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Страна (для учета местных стандартов)
                    </label>
                    <select 
                        id="country" 
                        value={country} 
                        onChange={(e) => setCountry(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    >
                        <option value="Россия">Россия</option>
                        <option value="США">США</option>
                        <option value="ЕС">Европейский Союз</option>
                        <option value="Китай">Китай</option>
                        <option value="Япония">Япония</option>
                    </select>
                </div>
                <button 
                    type="submit" 
                    disabled={isLoading}
                    style={{
                        backgroundColor: isLoading ? '#cccccc' : '#007bff',
                        color: 'white',
                        border: 'none',
                        padding: '0.75rem 1.5rem',
                        fontSize: '1rem',
                        cursor: isLoading ? 'not-allowed' : 'pointer'
                    }}
                >
                    {isLoading ? 'Генерация рекомендаций...' : 'Получить рекомендации'}
                </button>
            </form>
            {recommendation && (
                <div className="recommendation-result" style={{marginTop: '2rem', border: '1px solid #ddd', padding: '1rem', borderRadius: '4px'}}>
                    <h3 style={{marginTop: '0'}}>Рекомендации по здоровью</h3>
                    <div style={{display: 'flex', gap: '1rem', marginBottom: '1rem'}}>
                        <span style={{fontWeight: 'bold'}}>Симптомы:</span>
                        <span>{recommendation.symptoms}</span>
                    </div>
                    {recommendation.age && (
                        <div style={{display: 'flex', gap: '1rem', marginBottom: '1rem'}}>
                            <span style={{fontWeight: 'bold'}}>Возраст:</span>
                            <span>{recommendation.age}</span>
                        </div>
                    )}
                    <div style={{display: 'flex', gap: '1rem', marginBottom: '1rem'}}>
                        <span style={{fontWeight: 'bold'}}>Пол:</span>
                        <span>{recommendation.gender}</span>
                    </div>
                    <div style={{display: 'flex', gap: '1rem', marginBottom: '1.5rem'}}>
                        <span style={{fontWeight: 'bold'}}>Страна:</span>
                        <span>{recommendation.country}</span>
                    </div>
                    <div 
                        className="recommendation-content" 
                        style={{
                            whiteSpace: 'pre-wrap',
                            lineHeight: '1.6',
                            fontFamily: 'Arial, sans-serif',
                            backgroundColor: '#f8f9fa',
                            padding: '1rem',
                            borderRadius: '4px'
                        }}
                    >
                        {recommendation.recommendation}
                    </div>
                </div>
            )}
        </div>
    );
}

export default HealthRecommendationForm;