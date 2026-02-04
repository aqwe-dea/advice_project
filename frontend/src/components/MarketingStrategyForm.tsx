import React, { useState } from 'react';
import axios from 'axios';

function MarketingStrategyForm() {
    const [idea, setIdea] = useState<string>('');
    const [targetAudience, setTargetAudience] = useState<string>('широкая аудитория');
    const [budget, setBudget] = useState<string>('средний');
    const [timeframe, setTimeframe] = useState<string>('3 месяца');
    const [country, setCountry] = useState<string>('Россия');
    const [platform, setPlatform] = useState<string>('многофункциональная');
    const [strategy, setStrategy] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!idea.trim()) {
            setError('Пожалуйста, укажите вашу идею');
            return;
        }
        setIsLoading(true);
        setError('');
        try {
            const response = await axios.post(
                'http://advice-project.onrender.com/marketing-strategy/',
                { 
                    idea, 
                    target_audience: targetAudience,
                    budget,
                    timeframe,
                    country,
                    platform
                },
                { 
                    headers: {
                        "Content-Type": "application/json",
                        "X-GitHub-Api-Version": "2022-11-28",
                        "Accept": "application/vnd.github+json" 
                    }
                }
            );
            setStrategy(response.data);
        } catch (err: any) {
            console.error('Ошибка генерации маркетинговой стратегии:', err);
            if (err.response) {
                setError(`Ошибка ${err.response.status}: ${err.response.data.error || 'Не удалось сгенерировать стратегию'}`);
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
        <div className="marketing-strategy-form" style={{maxWidth: '1000px', margin: '2rem auto', padding: '2rem', backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.15)'}}>
            <h2 style={{textAlign: 'center', marginBottom: '1.5rem', color: '#7a6ac8', fontSize: '2.2rem'}}>Стратегия продвижения идей</h2>
            <p style={{textAlign: 'center', marginBottom: '2rem', color: '#e8e8d3', fontSize: '1.1rem'}}>
                Получите персонализированную стратегию продвижения вашей идеи с конкретными шагами и рекомендациями
            </p>
            {error && (
                <div className="error-message" style={{color: 'red', marginBottom: '1.5rem', padding: '1rem', backgroundColor: 'rgba(255, 0, 0, 0.1)', borderRadius: '8px'}}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit} style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem'}}>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="idea" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Ваша идея
                    </label>
                    <textarea
                        id="idea"
                        placeholder="Опишите вашу идею подробно"
                        value={idea}
                        onChange={(e) => setIdea(e.target.value)}
                        style={{width: '100%', height: '150px', padding: '1rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    />
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="target-audience" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Целевая аудитория
                    </label>
                    <select 
                        id="target-audience" 
                        value={targetAudience} 
                        onChange={(e) => setTargetAudience(e.target.value)}
                        style={{width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    >
                        <option value="широкая аудитория">Широкая аудитория</option>
                        <option value="молодежь (18-25)">Молодежь (18-25)</option>
                        <option value="профессионалы (25-40)">Профессионалы (25-40)</option>
                        <option value="предприниматели">Предприниматели</option>
                        <option value="родители">Родители</option>
                        <option value="специфическая ниша">Специфическая ниша</option>
                    </select>
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="budget" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Бюджет
                    </label>
                    <select 
                        id="budget" 
                        value={budget} 
                        onChange={(e) => setBudget(e.target.value)}
                        style={{width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    >
                        <option value="низкий">Низкий (до 50 тыс. руб.)</option>
                        <option value="средний">Средний (50-200 тыс. руб.)</option>
                        <option value="высокий">Высокий (свыше 200 тыс. руб.)</option>
                        <option value="ограниченный">Ограниченный (только органический рост)</option>
                    </select>
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="timeframe" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Временные рамки
                    </label>
                    <select 
                        id="timeframe" 
                        value={timeframe} 
                        onChange={(e) => setTimeframe(e.target.value)}
                        style={{width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    >
                        <option value="1 месяц">1 месяц</option>
                        <option value="3 месяца">3 месяца</option>
                        <option value="6 месяцев">6 месяцев</option>
                        <option value="1 год">1 год</option>
                        <option value="долгосрочная">Долгосрочная (свыше 1 года)</option>
                    </select>
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="country" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Страна
                    </label>
                    <select 
                        id="country" 
                        value={country} 
                        onChange={(e) => setCountry(e.target.value)}
                        style={{width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    >
                        <option value="Россия">Россия</option>
                        <option value="США">США</option>
                        <option value="ЕС">Европейский Союз</option>
                        <option value="Китай">Китай</option>
                        <option value="Япония">Япония</option>
                        <option value="мировой рынок">Мировой рынок</option>
                    </select>
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="platform" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Платформа
                    </label>
                    <select 
                        id="platform" 
                        value={platform} 
                        onChange={(e) => setPlatform(e.target.value)}
                        style={{width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    >
                        <option value="многофункциональная">Многофункциональная</option>
                        <option value="социальные сети">Социальные сети</option>
                        <option value="поисковые системы">Поисковые системы</option>
                        <option value="офлайн">Офлайн</option>
                        <option value="нишевые платформы">Нишевые платформы</option>
                    </select>
                </div>
                <div style={{gridColumn: '1 / -1', textAlign: 'center'}}>
                    <button 
                        type="submit" 
                        disabled={isLoading}
                        style={{
                            backgroundColor: isLoading ? '#cccccc' : '#7a6ac8',
                            color: 'white',
                            border: 'none',
                            padding: '0.85rem 2.5rem',
                            fontSize: '1.1rem',
                            borderRadius: '8px',
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            fontWeight: 'bold',
                            boxShadow: isLoading ? 'none' : '0 4px 15px rgba(122, 106, 200, 0.3)'
                        }}
                    >
                        {isLoading ? 'Генерация стратегии...' : 'Создать стратегию продвижения'}
                    </button>
                </div>
            </form>
            {strategy && (
                <div className="strategy-result" style={{marginTop: '3rem', backgroundColor: 'rgba(255, 255, 255, 0.07)', borderRadius: '12px', padding: '2rem', boxShadow: '0 4px 15px rgba(0,0,0,0.1)'}}>
                    <h3 style={{margin: '0 0 1.5rem 0', color: '#7a6ac8', fontSize: '2rem'}}>Маркетинговая стратегия для "{strategy.idea}"</h3>
                    <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem'}}>
                        <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.2rem', borderRadius: '8px'}}>
                            <strong style={{color: '#e8e8d3', display: 'block', marginBottom: '0.3rem'}}>Целевая аудитория:</strong>
                            <span style={{color: '#f8f8f0'}}>{strategy.target_audience}</span>
                        </div>
                        <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.2rem', borderRadius: '8px'}}>
                            <strong style={{color: '#e8e8d3', display: 'block', marginBottom: '0.3rem'}}>Бюджет:</strong>
                            <span style={{color: '#f8f8f0'}}>{strategy.budget}</span>
                        </div>
                        <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.2rem', borderRadius: '8px'}}>
                            <strong style={{color: '#e8e8d3', display: 'block', marginBottom: '0.3rem'}}>Временные рамки:</strong>
                            <span style={{color: '#f8f8f0'}}>{strategy.timeframe}</span>
                        </div>
                        <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.2rem', borderRadius: '8px'}}>
                            <strong style={{color: '#e8e8d3', display: 'block', marginBottom: '0.3rem'}}>Страна:</strong>
                            <span style={{color: '#f8f8f0'}}>{strategy.country}</span>
                        </div>
                    </div>
                    <div 
                        className="strategy-content" 
                        style={{
                            whiteSpace: 'pre-wrap',
                            lineHeight: '1.7',
                            fontFamily: 'Arial, sans-serif',
                            backgroundColor: 'rgba(0, 0, 0, 0.1)',
                            padding: '1.5rem',
                            borderRadius: '10px',
                            color: '#f8f8f0'
                        }}
                    >
                        {strategy.marketing_strategy}
                    </div>
                    <div style={{marginTop: '2rem', textAlign: 'center', padding: '1.5rem', backgroundColor: 'rgba(122, 106, 200, 0.1)', borderRadius: '10px'}}>
                        <p style={{color: '#e8e8d3', marginBottom: '1rem'}}>
                            Эта стратегия была сгенерирована с использованием передовых моделей искусственного интеллекта и профессиональных маркетинговых знаний.
                        </p>
                        <button style={{
                            backgroundColor: '#7a6ac8',
                            color: 'white',
                            border: 'none',
                            padding: '0.75rem 1.5rem',
                            fontSize: '1rem',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontWeight: 'bold'
                        }}>
                            Скачать стратегию в PDF
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default MarketingStrategyForm;