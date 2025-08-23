import React, { useState } from 'react';
import axios from 'axios';

function TravelPlannerForm() {
    const [destination, setDestination] = useState<string>('');
    const [budget, setBudget] = useState<string>('средний');
    const [travelDates, setTravelDates] = useState<string>('июль-август');
    const [travelStyle, setTravelStyle] = useState<string>('активный отдых');
    const [groupType, setGroupType] = useState<string>('один/одна');
    const [specialInterests, setSpecialInterests] = useState<string>('общие');
    const [plan, setPlan] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!destination.trim()) {
            setError('Пожалуйста, укажите место назначения');
            return;
        }
        setIsLoading(true);
        setError('');
        try {
            const response = await axios.post(
                'https://advice-project.onrender.com/travel-planner/',
                { 
                    destination,
                    budget,
                    travel_dates: travelDates,
                    travel_style: travelStyle,
                    group_type: groupType,
                    special_interests: specialInterests
                },
                { 
                    headers: { 'Content-Type': 'application/json' },
                    timeout: 45000
                }
            );
            setPlan(response.data);
        } catch (err: any) {
            console.error('Ошибка генерации плана путешествия:', err);
            if (err.response) {
                setError(`Ошибка ${err.response.status}: ${err.response.data.error || 'Не удалось сгенерировать план'}`);
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
        <div className="travel-planner-form" style={{maxWidth: '1000px', margin: '2rem auto', padding: '2rem', backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.15)'}}>
            <h2 style={{textAlign: 'center', marginBottom: '1.5rem', color: '#7a6ac8', fontSize: '2.2rem'}}>Персонализированный планировщик путешествий</h2>
            <p style={{textAlign: 'center', marginBottom: '2rem', color: '#e8e8d3', fontSize: '1.1rem'}}>
                Получите уникальный маршрут путешествия, созданный специально для вас с учетом ваших предпочтений и бюджета
            </p>
            {error && (
                <div className="error-message" style={{color: 'red', marginBottom: '1.5rem', padding: '1rem', backgroundColor: 'rgba(255, 0, 0, 0.1)', borderRadius: '8px'}}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit} style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem'}}>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="destination" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Место назначения
                    </label>
                    <input
                        type="text"
                        id="destination"
                        placeholder="Например: Париж, Токио, Бали"
                        value={destination}
                        onChange={(e) => setDestination(e.target.value)}
                        style={{width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    />
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
                        <option value="низкий">Низкий (эконом-вариант)</option>
                        <option value="средний">Средний (комфорт)</option>
                        <option value="высокий">Высокий (премиум)</option>
                        <option value="люкс">Люкс (VIP-уровень)</option>
                    </select>
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="travel-dates" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Даты путешествия
                    </label>
                    <input
                        type="text"
                        id="travel-dates"
                        placeholder="Например: июль-август, 15-25 сентября"
                        value={travelDates}
                        onChange={(e) => setTravelDates(e.target.value)}
                        style={{width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    />
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="travel-style" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Стиль путешествия
                    </label>
                    <select 
                        id="travel-style" 
                        value={travelStyle} 
                        onChange={(e) => setTravelStyle(e.target.value)}
                        style={{width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    >
                        <option value="активный отдых">Активный отдых</option>
                        <option value="культурный туризм">Культурный туризм</option>
                        <option value="гастрономический">Гастрономический</option>
                        <option value="отдых на пляже">Отдых на пляже</option>
                        <option value="экстремальный туризм">Экстремальный туризм</option>
                        <option value="спа и релакс">Спа и релакс</option>
                    </select>
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="group-type" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Тип группы
                    </label>
                    <select 
                        id="group-type" 
                        value={groupType} 
                        onChange={(e) => setGroupType(e.target.value)}
                        style={{width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    >
                        <option value="один/одна">Один/одна</option>
                        <option value="пара">Пара</option>
                        <option value="семья с детьми">Семья с детьми</option>
                        <option value="группа друзей">Группа друзей</option>
                        <option value="бизнес-поездка">Бизнес-поездка</option>
                    </select>
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="special-interests" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Специальные интересы
                    </label>
                    <select 
                        id="special-interests" 
                        value={specialInterests} 
                        onChange={(e) => setSpecialInterests(e.target.value)}
                        style={{width: '100%', padding: '0.75rem', fontSize: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.1)', color: '#f8f8f0'}}
                    >
                        <option value="общие">Общие</option>
                        <option value="история и архитектура">История и архитектура</option>
                        <option value="современное искусство">Современное искусство</option>
                        <option value="природа и экология">Природа и экология</option>
                        <option value="шопинг">Шопинг</option>
                        <option value="ночная жизнь">Ночная жизнь</option>
                        <option value="здоровый образ жизни">Здоровый образ жизни</option>
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
                        {isLoading ? 'Генерация маршрута...' : 'Создать маршрут путешествия'}
                    </button>
                </div>
            </form>
            {plan && (
                <div className="plan-result" style={{marginTop: '3rem', backgroundColor: 'rgba(255, 255, 255, 0.07)', borderRadius: '12px', padding: '2rem', boxShadow: '0 4px 15px rgba(0,0,0,0.1)'}}>
                    <h3 style={{margin: '0 0 1.5rem 0', color: '#7a6ac8', fontSize: '2rem'}}>Путешествие в {plan.destination}</h3>
                    <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem'}}>
                        <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.2rem', borderRadius: '8px'}}>
                            <strong style={{color: '#e8e8d3', display: 'block', marginBottom: '0.3rem'}}>Бюджет:</strong>
                            <span style={{color: '#f8f8f0'}}>{plan.budget}</span>
                        </div>
                        <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.2rem', borderRadius: '8px'}}>
                            <strong style={{color: '#e8e8d3', display: 'block', marginBottom: '0.3rem'}}>Даты:</strong>
                            <span style={{color: '#f8f8f0'}}>{plan.travel_dates}</span>
                        </div>
                        <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.2rem', borderRadius: '8px'}}>
                            <strong style={{color: '#e8e8d3', display: 'block', marginBottom: '0.3rem'}}>Стиль:</strong>
                            <span style={{color: '#f8f8f0'}}>{plan.travel_style}</span>
                        </div>
                        <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.2rem', borderRadius: '8px'}}>
                            <strong style={{color: '#e8e8d3', display: 'block', marginBottom: '0.3rem'}}>Группа:</strong>
                            <span style={{color: '#f8f8f0'}}>{plan.group_type}</span>
                        </div>
                    </div>
                    <div 
                        className="plan-content" 
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
                        {plan.travel_plan}
                    </div>
                    <div style={{marginTop: '2rem', textAlign: 'center', padding: '1.5rem', backgroundColor: 'rgba(122, 106, 200, 0.1)', borderRadius: '10px'}}>
                        <p style={{color: '#e8e8d3', marginBottom: '1rem'}}>
                            Этот маршрут был сгенерирован с использованием передовых моделей искусственного интеллекта и данных о туристических направлениях со всего мира.
                        </p>
                        <div style={{display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap'}}>
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
                                Скачать маршрут в PDF
                            </button>
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
                                Добавить в календарь
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default TravelPlannerForm;