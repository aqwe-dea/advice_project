import React, { useState, useEffect } from 'react';
import axios from 'axios';

function SessionPurchase() {
    const [duration, setDuration] = useState<number>(1);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const [sessionStatus, setSessionStatus] = useState<any>(null);
    const [countdown, setCountdown] = useState<number>(0);
    // Проверяем статус сессии при загрузке
    useEffect(() => {
        checkSessionStatus();
        // Периодически проверяем статус сессии
        const interval = setInterval(checkSessionStatus, 5000);
        return () => clearInterval(interval);
    }, []);
    // Обновляем обратный отсчет
    useEffect(() => {
        if (sessionStatus && sessionStatus.is_active && sessionStatus.remaining_time > 0) {
            setCountdown(sessionStatus.remaining_time);
            const countdownInterval = setInterval(() => {
                setCountdown(prev => {
                    if (prev <= 1) {
                        clearInterval(countdownInterval);
                        checkSessionStatus();
                        return 0;
                    }
                    return prev - 1;
                });
            }, 1000);
            return () => clearInterval(countdownInterval);
        }
    }, [sessionStatus]);
    const checkSessionStatus = async () => {
        try {
            const response = await axios.get(
                'https://advice-project.onrender.com/session-status/',
                { withCredentials: true }
            );
            setSessionStatus(response.data);
        } catch (err: any) {
            console.error('Ошибка проверки статуса сессии:', err);
            setSessionStatus(null);
        }
    };
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (duration < 1 || duration > 168) {
            setError('Продолжительность сессии должна быть от 1 до 168 часов');
            return;
        }
        setIsLoading(true);
        setError('');
        try {
            const response = await axios.post(
                'https://advice-project.onrender.com/create-checkout-session/',
                { duration },
                { 
                    headers: { 'Content-Type': 'application/json' },
                    timeout: 30000
                }
            );
            
            // Перенаправляем пользователя на страницу оплаты Stripe
            window.location.href = response.data.url;
        } catch (err: any) {
            console.error('Ошибка создания сессии оплаты:', err);
            setError('Не удалось создать сессию оплаты. Попробуйте позже.');
        } finally {
            setIsLoading(false);
        }
    };
    const formatTime = (seconds: number) => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };
    // Если сессия активна, показываем информацию о ней
    if (sessionStatus && sessionStatus.is_active) {
        return (
            <div style={{
                maxWidth: '500px',
                margin: '2rem auto',
                padding: '2rem',
                backgroundColor: 'rgba(255, 255, 255, 0.07)',
                borderRadius: '12px',
                boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
                textAlign: 'center'
            }}>
                <div style={{
                    fontSize: '5rem',
                    color: '#7a6ac8',
                    marginBottom: '1rem'
                }}>
                    ⏳
                </div>
                <h2 style={{
                    fontSize: '2rem',
                    marginBottom: '1rem',
                    color: '#7a6ac8'
                }}>
                    Ваша сессия активна
                </h2>
                <p style={{
                    fontSize: '1.2rem',
                    marginBottom: '1.5rem',
                    color: '#e8e8d3'
                }}>
                    Оставшееся время: <strong style={{color: '#f8f8f0'}}>{formatTime(countdown)}</strong>
                </p>
                <div style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    borderRadius: '10px',
                    padding: '1rem',
                    marginBottom: '1.5rem'
                }}>
                    <p style={{margin: '0.5rem 0', color: '#e8e8d3'}}>
                        Продолжительность: <strong style={{color: '#f8f8f0'}}>{sessionStatus.duration_hours} час{sessionStatus.duration_hours === 1 ? '' : 'а'}</strong>
                    </p>
                    <p style={{margin: '0.5rem 0', color: '#e8e8d3'}}>
                        Заканчивается: <strong style={{color: '#f8f8f0'}}>{new Date(sessionStatus.expires_at).toLocaleString()}</strong>
                    </p>
                </div>
                <button 
                    onClick={checkSessionStatus}
                    style={{
                        backgroundColor: '#4a14e0',
                        color: 'white',
                        border: 'none',
                        padding: '0.75rem 1.5rem',
                        fontSize: '1rem',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontWeight: 'bold'
                    }}
                >
                    Обновить статус
                </button>
            </div>
        );
    }
    // Если сессия неактивна, показываем форму покупки
    return (
        <div className="session-purchase" style={{maxWidth: '500px', margin: '2rem auto', padding: '2rem', backgroundColor: 'rgba(255, 255, 255, 0.07)', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.15)'}}>
            <h2 style={{textAlign: 'center', marginBottom: '1.5rem', color: '#7a6ac8', fontSize: '2.2rem'}}>Покупка сессии доступа</h2>
            <p style={{textAlign: 'center', marginBottom: '2rem', color: '#e8e8d3', fontSize: '1.1rem'}}>
                Получите доступ ко всем 15 профессиональным услугам на выбранное время
            </p>
            {error && (
                <div className="error-message" style={{color: 'red', marginBottom: '1.5rem', padding: '1rem', backgroundColor: 'rgba(255, 0, 0, 0.1)', borderRadius: '8px'}}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit} style={{display: 'flex', flexDirection: 'column', gap: '1.5rem'}}>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="duration" style={{display: 'block', marginBottom: '0.5rem', color: '#f8f8f0', fontWeight: '500'}}>
                        Продолжительность сессии (часы)
                    </label>
                    <input
                        type="number"
                        id="duration"
                        min="1"
                        max="168"
                        value={duration}
                        onChange={(e) => setDuration(parseInt(e.target.value))}
                        style={{
                            width: '100%',
                            padding: '0.75rem',
                            fontSize: '1rem',
                            borderRadius: '8px',
                            border: '1px solid rgba(255, 255, 255, 0.2)',
                            backgroundColor: 'rgba(0, 0, 0, 0.1)',
                            color: '#f8f8f0'
                        }}
                    />
                    <div style={{fontSize: '0.8rem', color: '#777', marginTop: '0.5rem'}}>
                        Выберите от 1 до 168 часов (1 неделя)
                    </div>
                </div>
                <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1rem', borderRadius: '8px'}}>
                    <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem'}}>
                        <span style={{color: '#e8e8d3'}}>Цена:</span>
                        <strong style={{color: '#f8f8f0'}}>{duration * 10} ₽</strong>
                    </div>
                    <div style={{display: 'flex', justifyContent: 'space-between'}}>
                        <span style={{color: '#e8e8d3'}}>Стоимость за час:</span>
                        <span style={{color: '#f8f8f0'}}>10 ₽</span>
                    </div>
                </div>
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
                    {isLoading ? 'Подготовка к оплате...' : `Купить доступ на ${duration} часов`}
                </button>
            </form>
            <div style={{marginTop: '2rem', padding: '1.5rem', backgroundColor: 'rgba(122, 106, 200, 0.1)', borderRadius: '10px'}}>
                <h3 style={{margin: '0 0 0.5rem 0', color: '#7a6ac8', fontSize: '1.3rem'}}>Почему стоит купить сессию?</h3>
                <ul style={{textAlign: 'left', paddingLeft: '1.5rem', color: '#e8e8d3', lineHeight: '1.6'}}>
                    <li>Полный доступ ко всем 15 профессиональным услугам</li>
                    <li>Нет скрытых платежей или подписок</li>
                    <li>Оплата только за то время, которое вам нужно</li>
                    <li>Мгновенная активация после оплаты</li>
                </ul>
            </div>
        </div>
    );
}

export default SessionPurchase;