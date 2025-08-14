import React, { useState } from 'react';
import axios from 'axios';

function InvestmentAnalysisForm() {
    const [initialInvestment, setInitialInvestment] = useState<string>('');
    const [expectedReturn, setExpectedReturn] = useState<string>('');
    const [investmentPeriod, setInvestmentPeriod] = useState<string>('');
    const [riskLevel, setRiskLevel] = useState<string>('средний');
    const [investmentType, setInvestmentType] = useState<string>('акции');
    const [country, setCountry] = useState<string>('Россия');
    const [analysis, setAnalysis] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!initialInvestment || !expectedReturn || !investmentPeriod) {
            setError('Пожалуйста, заполните все обязательные поля');
            return;
        }
        setIsLoading(true);
        setError('');
        try {
            const response = await axios.post(
                'https://advice-project.onrender.com/investment-analysis/',
                { 
                    initial_investment: initialInvestment,
                    expected_return: expectedReturn,
                    investment_period: investmentPeriod,
                    risk_level: riskLevel,
                    investment_type: investmentType,
                    country: country
                },
                { 
                    headers: { 'Content-Type': 'application/json' },
                    timeout: 30000
                }
            );
            setAnalysis(response.data);
        } catch (err: any) {
            console.error('Ошибка анализа инвестиций:', err);
            if (err.response) {
                setError(`Ошибка ${err.response.status}: ${err.response.data.error || 'Не удалось проанализировать инвестиции'}`);
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
        <div className="investment-analysis-form">
            <h2>Анализ инвестиций на потенциальный доход</h2>
            <p>Введите параметры ваших инвестиций, и АКВИ проанализирует их потенциальную доходность и риски.</p>
            {error && (
                <div className="error-message" style={{color: 'red', marginBottom: '1rem'}}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit}>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="initial-investment" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Начальные инвестиции (в вашей валюте)
                    </label>
                    <input
                        type="number"
                        id="initial-investment"
                        placeholder="Например: 100000"
                        value={initialInvestment}
                        onChange={(e) => setInitialInvestment(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    />
                </div>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="expected-return" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Ожидаемая годовая доходность (%)
                    </label>
                    <input
                        type="number"
                        id="expected-return"
                        placeholder="Например: 8.5"
                        value={expectedReturn}
                        onChange={(e) => setExpectedReturn(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    />
                </div>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="investment-period" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Период инвестирования (в годах)
                    </label>
                    <input
                        type="number"
                        id="investment-period"
                        placeholder="Например: 5"
                        value={investmentPeriod}
                        onChange={(e) => setInvestmentPeriod(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    />
                </div>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="risk-level" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Уровень риска
                    </label>
                    <select 
                        id="risk-level" 
                        value={riskLevel} 
                        onChange={(e) => setRiskLevel(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    >
                        <option value="низкий">Низкий</option>
                        <option value="средний">Средний</option>
                        <option value="высокий">Высокий</option>
                    </select>
                </div>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="investment-type" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Тип инвестиций
                    </label>
                    <select 
                        id="investment-type" 
                        value={investmentType} 
                        onChange={(e) => setInvestmentType(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    >
                        <option value="акции">Акции</option>
                        <option value="облигации">Облигации</option>
                        <option value="недвижимость">Недвижимость</option>
                        <option value="криптовалюты">Криптовалюты</option>
                        <option value="стартапы">Инвестиции в стартапы</option>
                        <option value="другое">Другое</option>
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
                    {isLoading ? 'Анализ инвестиций...' : 'Проанализировать инвестиции'}
                </button>
            </form>
            {analysis && (
                <div className="analysis-result" style={{marginTop: '2rem', border: '1px solid #ddd', padding: '1rem', borderRadius: '4px'}}>
                    <h3 style={{marginTop: '0'}}>Результат анализа инвестиций</h3>
                    <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '1.5rem'}}>
                        <div style={{border: '1px solid #eee', padding: '1rem', borderRadius: '4px'}}>
                            <h4 style={{margin: '0 0 0.5rem 0'}}>Начальные инвестиции</h4>
                            <p style={{fontSize: '1.2rem', fontWeight: 'bold'}}>{analysis.initial_investment}</p>
                        </div>
                        <div style={{border: '1px solid #eee', padding: '1rem', borderRadius: '4px'}}>
                            <h4 style={{margin: '0 0 0.5rem 0'}}>Ожидаемая доходность</h4>
                            <p style={{fontSize: '1.2rem', fontWeight: 'bold'}}>{analysis.expected_return}% в год</p>
                        </div>
                        <div style={{border: '1px solid #eee', padding: '1rem', borderRadius: '4px'}}>
                            <h4 style={{margin: '0 0 0.5rem 0'}}>Период</h4>
                            <p style={{fontSize: '1.2rem', fontWeight: 'bold'}}>{analysis.investment_period} лет</p>
                        </div>
                    </div>
                    <div style={{border: '1px solid #eee', padding: '1rem', borderRadius: '4px'}}>
                        <h4 style={{margin: '0 0 0.5rem 0'}}>Уровень риска</h4>
                        <p style={{
                            fontSize: '1.2rem', 
                            fontWeight: 'bold',
                            color: analysis.risk_level === 'низкий' ? 'green' : analysis.risk_level === 'средний' ? 'orange' : 'red'
                        }}>
                            {analysis.risk_level}
                        </p>
                    </div>
                    <div 
                        className="analysis-content" 
                        style={{
                            whiteSpace: 'pre-wrap',
                            lineHeight: '1.6',
                            fontFamily: 'Arial, sans-serif',
                            backgroundColor: '#f8f9fa',
                            padding: '1rem',
                            borderRadius: '4px',
                            marginTop: '1.5rem'
                        }}
                    >
                        {analysis.analysis}
                    </div>
                </div>
            )}
        </div>
    );
}

export default InvestmentAnalysisForm;