import React, { useState } from 'react';
import axios from 'axios';

function CompetitorAnalysisForm() {
    const [businessName, setBusinessName] = useState<string>('');
    const [businessDescription, setBusinessDescription] = useState<string>('');
    const [competitors, setCompetitors] = useState<string>('');
    const [marketSegment, setMarketSegment] = useState<string>('общий рынок');
    const [country, setCountry] = useState<string>('Россия');
    const [analysis, setAnalysis] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!businessName.trim() || !businessDescription.trim()) {
            setError('Пожалуйста, укажите название бизнеса и его описание');
            return;
        }
        setIsLoading(true);
        setError('');
        try {
            const response = await axios.post(
                'https://advice-project.onrender.com/competitor-analysis/',
                { 
                    business_name: businessName,
                    business_description: businessDescription,
                    competitors,
                    market_segment: marketSegment,
                    country
                },
                { 
                    headers: { 'Content-Type': 'application/json' }
                }
            );
            setAnalysis(response.data);
        } catch (err: any) {
            console.error('Ошибка анализа конкурентов:', err);
            if (err.response) {
                setError(`Ошибка ${err.response.status}: ${err.response.data.error || 'Не удалось проанализировать конкурентов'}`);
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
        <div className="competitor-analysis-form" style={{maxWidth: '1000px', margin: '2rem auto', padding: '2rem', backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.15)'}}>
            <h2 style={{textAlign: 'center', marginBottom: '1.5rem', color: '#4a14e0', fontSize: '2.2rem'}}>Анализ конкурентов в реальном времени</h2>
            <p style={{textAlign: 'center', marginBottom: '2rem', color: '#e8e8d3', fontSize: '1.1rem'}}>
                Получите глубокий анализ ваших конкурентов с конкретными рекомендациями по улучшению вашей позиции на рынке
            </p>
            {error && (
                <div className="error-message" style={{color: 'red', marginBottom: '1.5rem', padding: '1rem', backgroundColor: 'rgba(255, 0, 0, 0.1)', borderRadius: '8px'}}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit} style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem'}}>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="business-name" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Название вашего бизнеса
                    </label>
                    <input
                        type="text"
                        id="business-name"
                        placeholder="Например: 'Кофейня у дома'"
                        value={businessName}
                        onChange={(e) => setBusinessName(e.target.value)}
                        style={{width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    />
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="business-description" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Описание вашего бизнеса
                    </label>
                    <textarea
                        id="business-description"
                        placeholder="Опишите ваш бизнес, ваши услуги или продукты"
                        value={businessDescription}
                        onChange={(e) => setBusinessDescription(e.target.value)}
                        style={{width: '100%', height: '120px', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    />
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="competitors" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Ваши основные конкуренты
                    </label>
                    <textarea
                        id="competitors"
                        placeholder="Перечислите названия конкурентов через запятую"
                        value={competitors}
                        onChange={(e) => setCompetitors(e.target.value)}
                        style={{width: '100%', height: '120px', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    />
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="market-segment" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Сегмент рынка
                    </label>
                    <select 
                        id="market-segment" 
                        value={marketSegment} 
                        onChange={(e) => setMarketSegment(e.target.value)}
                        style={{width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    >
                        <option value="общий рынок">Общий рынок</option>
                        <option value="премиум сегмент">Премиум сегмент</option>
                        <option value="эконом сегмент">Эконом сегмент</option>
                        <option value="нишевый рынок">Нишевый рынок</option>
                        <option value="онлайн-рынок">Онлайн-рынок</option>
                        <option value="офлайн-рынок">Офлайн-рынок</option>
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
                        <option value="международный">Международный</option>
                    </select>
                </div>
                <div style={{gridColumn: '1 / -1', textAlign: 'center'}}>
                    <button 
                        type="submit" 
                        disabled={isLoading}
                        style={{
                            backgroundColor: isLoading ? '#cccccc' : '#4a14e0',
                            color: 'white',
                            border: 'none',
                            padding: '0.85rem 2.5rem',
                            fontSize: '1.1rem',
                            borderRadius: '8px',
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            fontWeight: 'bold',
                            boxShadow: isLoading ? 'none' : '0 4px 15px rgba(74, 20, 224, 0.3)'
                        }}
                    >
                        {isLoading ? 'Анализ конкурентов...' : 'Провести анализ'}
                    </button>
                </div>
            </form>
            {analysis && (
                <div className="analysis-result" style={{marginTop: '3rem', backgroundColor: 'rgba(255, 255, 255, 0.07)', borderRadius: '12px', padding: '2rem', boxShadow: '0 4px 15px rgba(0,0,0,0.1)'}}>
                    <h3 style={{margin: '0 0 1.5rem 0', color: '#4a14e0', fontSize: '2rem'}}>Анализ конкурентов для "{analysis.business_name}"</h3>
                    <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem'}}>
                        <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.2rem', borderRadius: '8px'}}>
                            <strong style={{color: '#e8e8d3', display: 'block', marginBottom: '0.3rem'}}>Сегмент рынка:</strong>
                            <span style={{color: '#f8f8f0'}}>{analysis.market_segment}</span>
                        </div>
                        <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.2rem', borderRadius: '8px'}}>
                            <strong style={{color: '#e8e8d3', display: 'block', marginBottom: '0.3rem'}}>Страна:</strong>
                            <span style={{color: '#f8f8f0'}}>{analysis.country}</span>
                        </div>
                        <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.2rem', borderRadius: '8px'}}>
                            <strong style={{color: '#e8e8d3', display: 'block', marginBottom: '0.3rem'}}>Конкуренты:</strong>
                            <span style={{color: '#f8f8f0'}}>{analysis.competitors || 'Не указаны'}</span>
                        </div>
                    </div>
                    <div 
                        className="analysis-content" 
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
                        {analysis.analysis}
                    </div>
                    <div style={{marginTop: '2rem', textAlign: 'center', padding: '1.5rem', backgroundColor: 'rgba(74, 20, 224, 0.1)', borderRadius: '10px'}}>
                        <p style={{color: '#e8e8d3', marginBottom: '1rem'}}>
                            Этот анализ был сгенерирован с использованием передовых моделей искусственного интеллекта и данных о рынках со всего мира.
                        </p>
                        <div style={{display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap'}}>
                            <button style={{
                                backgroundColor: '#4a14e0',
                                color: 'white',
                                border: 'none',
                                padding: '0.75rem 1.5rem',
                                fontSize: '1rem',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                fontWeight: 'bold'
                            }}>
                                Скачать анализ в PDF
                            </button>
                            <button style={{
                                backgroundColor: '#3f00ff',
                                color: 'white',
                                border: 'none',
                                padding: '0.75rem 1.5rem',
                                fontSize: '1rem',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                fontWeight: 'bold'
                            }}>
                                Создать презентацию
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default CompetitorAnalysisForm;