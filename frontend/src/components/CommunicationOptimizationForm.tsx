import React, { useState } from 'react';
import axios from 'axios';

function CommunicationOptimizationForm() {
    const [companySize, setCompanySize] = useState<string>('500+ сотрудников');
    const [industry, setIndustry] = useState<string>('общая отрасль');
    const [communicationProblems, setCommunicationProblems] = useState<string>('');
    const [currentTools, setCurrentTools] = useState<string>('стандартные инструменты');
    const [goals, setGoals] = useState<string>('улучшение коммуникации');
    const [country, setCountry] = useState<string>('Россия');
    const [optimization, setOptimization] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!communicationProblems.trim()) {
            setError('Пожалуйста, опишите проблемы с коммуникацией');
            return;
        }
        setIsLoading(true);
        setError('');
        try {
            const response = await axios.post(
                '/communication-optimization/',
                { 
                    company_size: companySize,
                    industry,
                    communication_problems: communicationProblems,
                    current_tools: currentTools,
                    goals,
                    country
                },
                { 
                    headers: { 'Content-Type': 'application/json' },
                    timeout: 45000
                }
            );
            setOptimization(response.data);
        } catch (err: any) {
            console.error('Ошибка оптимизации коммуникации:', err);
            if (err.response) {
                setError(`Ошибка ${err.response.status}: ${err.response.data.error || 'Не удалось оптимизировать коммуникацию'}`);
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
        <div className="communication-optimization-form" style={{maxWidth: '1000px', margin: '2rem auto', padding: '2rem', backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.15)'}}>
            <h2 style={{textAlign: 'center', marginBottom: '1.5rem', color: '#3f00ff', fontSize: '2.2rem'}}>Оптимизация коммуникации в крупных организациях</h2>
            <p style={{textAlign: 'center', marginBottom: '2rem', color: '#e8e8d3', fontSize: '1.1rem'}}>
                Получите профессиональный анализ и стратегию оптимизации коммуникационных процессов в вашей компании
            </p>
            {error && (
                <div className="error-message" style={{color: 'red', marginBottom: '1.5rem', padding: '1rem', backgroundColor: 'rgba(255, 0, 0, 0.1)', borderRadius: '8px'}}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit} style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem'}}>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="company-size" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Размер компании
                    </label>
                    <select 
                        id="company-size" 
                        value={companySize} 
                        onChange={(e) => setCompanySize(e.target.value)}
                        style={{width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    >
                        <option value="50-200 сотрудников">50-200 сотрудников</option>
                        <option value="200-500 сотрудников">200-500 сотрудников</option>
                        <option value="500+ сотрудников">500+ сотрудников</option>
                        <option value="1000+ сотрудников">1000+ сотрудников</option>
                        <option value="многонациональная корпорация">Многонациональная корпорация</option>
                    </select>
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="industry" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Отрасль
                    </label>
                    <select 
                        id="industry" 
                        value={industry} 
                        onChange={(e) => setIndustry(e.target.value)}
                        style={{width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    >
                        <option value="общая отрасль">Общая отрасль</option>
                        <option value="финансовые услуги">Финансовые услуги</option>
                        <option value="IT и технологии">IT и технологии</option>
                        <option value="производство">Производство</option>
                        <option value="здравоохранение">Здравоохранение</option>
                        <option value="образование">Образование</option>
                        <option value="розничная торговля">Розничная торговля</option>
                        <option value="государственный сектор">Государственный сектор</option>
                    </select>
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem', gridColumn: '1 / -1'}}>
                    <label htmlFor="communication-problems" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Опишите проблемы с коммуникацией в вашей компании
                    </label>
                    <textarea
                        id="communication-problems"
                        placeholder="Опишите текущие проблемы с коммуникацией, с которыми сталкивается ваша компания"
                        value={communicationProblems}
                        onChange={(e) => setCommunicationProblems(e.target.value)}
                        style={{width: '100%', height: '150px', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    />
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="current-tools" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Текущие используемые инструменты
                    </label>
                    <textarea
                        id="current-tools"
                        placeholder="Опишите текущие инструменты коммуникации в вашей компании"
                        value={currentTools}
                        onChange={(e) => setCurrentTools(e.target.value)}
                        style={{width: '100%', height: '120px', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    />
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="goals" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Цели оптимизации
                    </label>
                    <select 
                        id="goals" 
                        value={goals} 
                        onChange={(e) => setGoals(e.target.value)}
                        style={{width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    >
                        <option value="улучшение коммуникации">Улучшение коммуникации</option>
                        <option value="снижение времени на коммуникацию">Снижение времени на коммуникацию</option>
                        <option value="повышение прозрачности">Повышение прозрачности процессов</option>
                        <option value="улучшение межотделного взаимодействия">Улучшение межотделного взаимодействия</option>
                        <option value="снижение ошибок из-за плохой коммуникации">Снижение ошибок из-за плохой коммуникации</option>
                        <option value="масштабирование коммуникационных процессов">Масштабирование коммуникационных процессов</option>
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
                            backgroundColor: isLoading ? '#cccccc' : '#3f00ff',
                            color: 'white',
                            border: 'none',
                            padding: '0.85rem 2.5rem',
                            fontSize: '1.1rem',
                            borderRadius: '8px',
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            fontWeight: 'bold',
                            boxShadow: isLoading ? 'none' : '0 4px 15px rgba(63, 0, 255, 0.3)'
                        }}
                    >
                        {isLoading ? 'Анализ коммуникации...' : 'Оптимизировать коммуникацию'}
                    </button>
                </div>
            </form>
            {optimization && (
                <div className="optimization-result" style={{marginTop: '3rem', backgroundColor: 'rgba(255, 255, 255, 0.07)', borderRadius: '12px', padding: '2rem', boxShadow: '0 4px 15px rgba(0,0,0,0.1)'}}>
                    <h3 style={{margin: '0 0 1.5rem 0', color: '#3f00ff', fontSize: '2rem'}}>Оптимизация коммуникации для компании</h3>
                    <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem'}}>
                        <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.2rem', borderRadius: '8px'}}>
                            <strong style={{color: '#e8e8d3', display: 'block', marginBottom: '0.3rem'}}>Размер компании:</strong>
                            <span style={{color: '#f8f8f0'}}>{optimization.company_size}</span>
                        </div>
                        <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.2rem', borderRadius: '8px'}}>
                            <strong style={{color: '#e8e8d3', display: 'block', marginBottom: '0.3rem'}}>Отрасль:</strong>
                            <span style={{color: '#f8f8f0'}}>{optimization.industry}</span>
                        </div>
                        <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.2rem', borderRadius: '8px'}}>
                            <strong style={{color: '#e8e8d3', display: 'block', marginBottom: '0.3rem'}}>Цели:</strong>
                            <span style={{color: '#f8f8f0'}}>{optimization.goals}</span>
                        </div>
                        <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.2rem', borderRadius: '8px'}}>
                            <strong style={{color: '#e8e8d3', display: 'block', marginBottom: '0.3rem'}}>Страна:</strong>
                            <span style={{color: '#f8f8f0'}}>{optimization.country}</span>
                        </div>
                    </div>
                    <div 
                        className="optimization-content" 
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
                        {optimization.optimization_plan}
                    </div>
                    <div style={{marginTop: '2rem', textAlign: 'center', padding: '1.5rem', backgroundColor: 'rgba(63, 0, 255, 0.1)', borderRadius: '10px'}}>
                        <p style={{color: '#e8e8d3', marginBottom: '1rem'}}>
                            Этот план оптимизации был сгенерирован с использованием передовых моделей искусственного интеллекта и данных о коммуникационных процессах в крупных организациях.
                        </p>
                        <div style={{display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap'}}>
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
                                Скачать план в PDF
                            </button>
                            <button style={{
                                backgroundColor: '#2e00b3',
                                color: 'white',
                                border: 'none',
                                padding: '0.75rem 1.5rem',
                                fontSize: '1rem',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                fontWeight: 'bold'
                            }}>
                                Создать дорожную карту
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default CommunicationOptimizationForm;