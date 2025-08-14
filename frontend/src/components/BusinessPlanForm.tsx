import React, { useState } from 'react';
import axios from 'axios';

function BusinessPlanForm() {
    const [idea, setIdea] = useState<string>('');
    const [businessType, setBusinessType] = useState<string>('стартап');
    const [country, setCountry] = useState<string>('Россия');
    const [plan, setPlan] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!idea.trim()) {
            setError('Пожалуйста, укажите идею бизнеса');
            return;
        }
        setIsLoading(true);
        setError('');
        try {
            const response = await axios.post(
                'https://advice-project.onrender.com/business-plan/',
                { idea, business_type: businessType, country },
                { 
                    headers: { 'Content-Type': 'application/json' },
                    timeout: 30000
                }
            );
            setPlan(response.data);
        } catch (err: any) {
            console.error('Ошибка генерации бизнес-плана:', err);
            if (err.response) {
                setError(`Ошибка ${err.response.status}: ${err.response.data.error || 'Не удалось сгенерировать бизнес-план'}`);
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
        <div className="business-plan-form">
            <h2>Генерация бизнес-планов и SWOT-анализа</h2>
            <p>Введите идею вашего бизнеса, и АКВИ создаст подробный бизнес-план с SWOT-анализом.</p>
            {error && (
                <div className="error-message" style={{color: 'red', marginBottom: '1rem'}}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit}>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="idea" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Идея бизнеса
                    </label>
                    <textarea
                        id="idea"
                        placeholder="Опишите вашу бизнес-идею"
                        value={idea}
                        onChange={(e) => setIdea(e.target.value)}
                        style={{width: '100%', height: '150px', padding: '0.5rem', fontSize: '1rem'}}
                    />
                </div>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="business-type" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Тип бизнеса
                    </label>
                    <select 
                        id="business-type" 
                        value={businessType} 
                        onChange={(e) => setBusinessType(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    >
                        <option value="стартап">Стартап</option>
                        <option value="малый бизнес">Малый бизнес</option>
                        <option value="средний бизнес">Средний бизнес</option>
                        <option value="крупный бизнес">Крупный бизнес</option>
                        <option value="франшиза">Франшиза</option>
                    </select>
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="country" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Страна
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
                    {isLoading ? 'Генерация плана...' : 'Создать бизнес-план'}
                </button>
            </form>
            {plan && (
                <div className="business-plan-result" style={{marginTop: '2rem', border: '1px solid #ddd', padding: '1rem', borderRadius: '4px'}}>
                    <h3 style={{marginTop: '0'}}>Бизнес-план: {plan.business_idea}</h3>
                    <div style={{display: 'flex', gap: '1rem', marginBottom: '1rem'}}>
                        <span style={{fontWeight: 'bold'}}>Тип бизнеса:</span>
                        <span>{plan.business_type}</span>
                    </div>
                    <div style={{display: 'flex', gap: '1rem', marginBottom: '1.5rem'}}>
                        <span style={{fontWeight: 'bold'}}>Страна:</span>
                        <span>{plan.country}</span>
                    </div>
                    <div 
                        className="business-plan-content" 
                        style={{
                            whiteSpace: 'pre-wrap',
                            lineHeight: '1.6',
                            fontFamily: 'Arial, sans-serif',
                            backgroundColor: '#f8f9fa',
                            padding: '1rem',
                            borderRadius: '4px'
                        }}
                    >
                        {plan.business_plan}
                    </div>
                </div>
            )}
        </div>
    );
}

export default BusinessPlanForm;