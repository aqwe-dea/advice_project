import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useLocation } from 'react-router-dom';

function PaymentSuccess() {
    const [sessionData, setSessionData] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string>('');
    const location = useLocation();
    useEffect(() => {
        const params = new URLSearchParams(location.search);
        const sessionId = params.get('session_id');
        if (!sessionId) {
            setError('Идентификатор сессии не найден');
            setIsLoading(false);
            return;
        }
        // Получаем данные о сессии
        axios.get(`https://advice-project.onrender.com/session-status/`)
            .then(response => {
                setSessionData(response.data);
                // Устанавливаем куки сессии
                document.cookie = `session_token=${response.data.session_token}; path=/; max-age=${response.data.remaining_time}; SameSite=Strict`;
            })
            .catch(err => {
                console.error('Ошибка получения данных о сессии:', err);
                setError('Не удалось получить данные о сессии');
            })
            .finally(() => {
                setIsLoading(false);
            });
    }, [location]);
    if (isLoading) {
        return (
            <div style={{
                maxWidth: '500px',
                margin: '4rem auto',
                padding: '2rem',
                backgroundColor: 'rgba(255, 255, 255, 0.07)',
                borderRadius: '12px',
                textAlign: 'center'
            }}>
                <div className="loading-spinner" style={{
                    fontSize: '3rem',
                    color: '#7a6ac8',
                    marginBottom: '1.5rem'
                }}>
                    ⏳
                </div>
                <h2 style={{
                    fontSize: '1.8rem',
                    marginBottom: '1rem',
                    color: '#7a6ac8'
                }}>
                    Подтверждение оплаты...
                </h2>
                <p style={{color: '#e8e8d3'}}>
                    Пожалуйста, подождите, пока мы обработаем ваш платеж
                </p>
            </div>
        );
    }
    if (error) {
        return (
            <div style={{
                maxWidth: '500px',
                margin: '4rem auto',
                padding: '2rem',
                backgroundColor: 'rgba(255, 255, 255, 0.07)',
                borderRadius: '12px',
                textAlign: 'center'
            }}>
                <div style={{
                    fontSize: '3rem',
                    color: 'red',
                    marginBottom: '1rem'
                }}>
                    ❌
                </div>
                <h2 style={{
                    fontSize: '1.8rem',
                    marginBottom: '1rem',
                    color: '#7a6ac8'
                }}>
                    Ошибка оплаты
                </h2>
                <p style={{color: '#e8e8d3', marginBottom: '1.5rem'}}>
                    {error}
                </p>
                <a href="/purchase-session" style={{
                    display: 'inline-block',
                    backgroundColor: '#7a6ac8',
                    color: 'white',
                    padding: '0.75rem 1.5rem',
                    borderRadius: '8px',
                    textDecoration: 'none',
                    fontWeight: 'bold'
                }}>
                    Попробовать снова
                </a>
            </div>
        );
    }
    if (sessionData && sessionData.is_active) {
        return (
            <div style={{
                maxWidth: '500px',
                margin: '4rem auto',
                padding: '2rem',
                backgroundColor: 'rgba(255, 255, 255, 0.07)',
                borderRadius: '12px',
                textAlign: 'center'
            }}>
                <div style={{
                    fontSize: '4rem',
                    color: '#4CAF50',
                    marginBottom: '1rem'
                }}>
                    ✅
                </div>
                <h2 style={{
                    fontSize: '2rem',
                    marginBottom: '1rem',
                    color: '#7a6ac8'
                }}>
                    Оплата успешна!
                </h2>
                <p style={{
                    fontSize: '1.2rem',
                    marginBottom: '1.5rem',
                    color: '#e8e8d3'
                }}>
                    Ваша сессия активна! Вы можете пользоваться всеми услугами Советницы АКВИ.
                </p>
                <div style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    borderRadius: '10px',
                    padding: '1.5rem',
                    marginBottom: '1.5rem'
                }}>
                    <p style={{margin: '0.5rem 0', color: '#e8e8d3'}}>
                        Продолжительность: <strong style={{color: '#f8f8f0'}}>{sessionData.duration_hours} час{sessionData.duration_hours === 1 ? '' : 'а'}</strong>
                    </p>
                    <p style={{margin: '0.5rem 0', color: '#e8e8d3'}}>
                        Заканчивается: <strong style={{color: '#f8f8f0'}}>{new Date(sessionData.expires_at).toLocaleString()}</strong>
                    </p>
                    <p style={{margin: '0.5rem 0', color: '#e8e8d3'}}>
                        Оставшееся время: <strong style={{color: '#f8f8f0'}}>{Math.floor(sessionData.remaining_time / 3600)} часов {Math.floor((sessionData.remaining_time % 3600) / 60)} минут</strong>
                    </p>
                </div>
                <div style={{display: 'flex', gap: '1rem', justifyContent: 'center'}}>
                    <a href="/" style={{
                        display: 'inline-block',
                        backgroundColor: '#4a14e0',
                        color: 'white',
                        padding: '0.75rem 1.5rem',
                        borderRadius: '8px',
                        textDecoration: 'none',
                        fontWeight: 'bold'
                    }}>
                        На главную
                    </a>
                    <a href="/purchase-session" style={{
                        display: 'inline-block',
                        backgroundColor: '#7a6ac8',
                        color: 'white',
                        padding: '0.75rem 1.5rem',
                        borderRadius: '8px',
                        textDecoration: 'none',
                        fontWeight: 'bold'
                    }}>
                        Продлить сессию
                    </a>
                </div>
            </div>
        );
    }
    return null;
}

export default PaymentSuccess;