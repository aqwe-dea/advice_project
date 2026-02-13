import React, { useState } from 'react';
import axios from 'axios';

function FinancialAnalysisForm() {
    const [financialData, setFinancialData] = useState<Array<{revenue: string, expenses: string}>>([
        {revenue: '', expenses: ''},
        {revenue: '', expenses: ''}
    ]);
    const [country, setCountry] = useState<string>('Россия');
    const [analysis, setAnalysis] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const [file, setFile] = useState<File | null>(null);
    const handleAddPeriod = () => {
        setFinancialData([...financialData, {revenue: '', expenses: ''}]);
    };
    const handleRemovePeriod = (index: number) => {
        if (financialData.length > 1) {
            const newData = [...financialData];
            newData.splice(index, 1);
            setFinancialData(newData);
        }
    };
    const handleDataChange = (index: number, field: string, value: string) => {
        const newData = [...financialData];
        newData[index] = {...newData[index], [field]: value};
        setFinancialData(newData);
    };
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const hasValidData = financialData.some(item => 
            item.revenue.trim() !== '' || item.expenses.trim() !== ''
        );        
        if (!hasValidData && !file) {
            setError('Пожалуйста, укажите финансовые данные или загрузите файл');
            return;
        }        
        setIsLoading(true);
        setError('');        
        try {
            let payload: any;
            if (file) {
                const formData = new FormData();
                formData.append('report', file);
                formData.append('country', country);
                payload = formData;
            } else {
                const data = financialData
                    .filter(item => item.revenue.trim() !== '' || item.expenses.trim() !== '')
                    .map(item => ({
                        revenue: parseFloat(item.revenue) || 0,
                        expenses: parseFloat(item.expenses) || 0
                    }));                
                payload = { data, country };
            }            
            const response = await axios.post(
                '/financial-analysis/',
                payload,
                { 
                    headers: { 
                        'Content-Type': file ? 'multipart/form-data' : 'application/json'
                    }
                }
            );            
            if (response.data.analysis) {
                setAnalysis(response.data);
            } else {
                setError('Сервер вернул пустой ответ. Попробуйте другие данные.');
            }
        } catch (err: any) {
            console.error('Ошибка финансового анализа:', err);            
            if (err.response) {
                setError(`Ошибка ${err.response.status}: ${err.response.data.error || 'Не удалось проанализировать данные'}`);
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
        <div className="financial-analysis-form">
            <h2>Финансовый анализ</h2>
            <p>Введите финансовые данные за периоды или загрузите отчет для анализа.</p>            
            {error && (
                <div className="error-message" style={{color: 'red', marginBottom: '1rem'}}>
                    {error}
                </div>
            )}            
            <form onSubmit={handleSubmit}>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="data-type" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Тип ввода
                    </label>
                    <select 
                        id="data-type" 
                        onChange={(e) => {
                            if (e.target.value === 'manual') {
                                setFile(null);
                            } else {
                                setFinancialData([{revenue: '', expenses: ''}, {revenue: '', expenses: ''}]);
                            }
                        }}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    >
                        <option value="manual">Ручной ввод</option>
                        <option value="file">Загрузка файла</option>
                    </select>
                </div>                
                {file && (
                    <div className="form-group" style={{marginBottom: '1rem'}}>
                        <label style={{display: 'block', marginBottom: '0.5rem'}}>
                            Загруженный файл: {file.name}
                        </label>
                        <button 
                            type="button" 
                            onClick={() => setFile(null)}
                            style={{
                                backgroundColor: '#dc3545',
                                color: 'white',
                                border: 'none',
                                padding: '0.25rem 0.5rem',
                                borderRadius: '4px',
                                cursor: 'pointer'
                            }}
                        >
                            Удалить файл
                        </button>
                    </div>
                )}                
                {!file && (
                    <div className="periods-container" style={{marginBottom: '1.5rem'}}>
                        <h3>Финансовые данные по периодам</h3>                        
                        {financialData.map((period, index) => (
                            <div key={index} className="period-row" style={{display: 'flex', gap: '1rem', marginBottom: '1rem', alignItems: 'center'}}>
                                <div style={{flex: 1}}>
                                    <label style={{display: 'block', marginBottom: '0.5rem'}}>
                                        Доход за период {index + 1}
                                    </label>
                                    <input
                                        type="number"
                                        placeholder="Доход"
                                        value={period.revenue}
                                        onChange={(e) => handleDataChange(index, 'revenue', e.target.value)}
                                        style={{width: '100%', padding: '0.5rem'}}
                                    />
                                </div>                                
                                <div style={{flex: 1}}>
                                    <label style={{display: 'block', marginBottom: '0.5rem'}}>
                                        Расходы за период {index + 1}
                                    </label>
                                    <input
                                        type="number"
                                        placeholder="Расходы"
                                        value={period.expenses}
                                        onChange={(e) => handleDataChange(index, 'expenses', e.target.value)}
                                        style={{width: '100%', padding: '0.5rem'}}
                                    />
                                </div>                                
                                <div style={{marginTop: '1.8rem'}}>
                                    {financialData.length > 1 && (
                                        <button 
                                            type="button"
                                            onClick={() => handleRemovePeriod(index)}
                                            style={{
                                                backgroundColor: '#dc3545',
                                                color: 'white',
                                                border: 'none',
                                                padding: '0.5rem',
                                                borderRadius: '4px',
                                                cursor: 'pointer'
                                            }}
                                        >
                                            Удалить
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}                        
                        <button 
                            type="button" 
                            onClick={handleAddPeriod}
                            style={{
                                backgroundColor: '#28a745',
                                color: 'white',
                                border: 'none',
                                padding: '0.5rem 1rem',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                marginBottom: '1rem'
                            }}
                        >
                            Добавить период
                        </button>
                    </div>
                )}                
                {!file && (
                    <div className="form-group" style={{marginBottom: '1rem'}}>
                        <label htmlFor="file-upload" style={{display: 'block', marginBottom: '0.5rem'}}>
                            Или загрузите файл
                        </label>
                        <input
                            type="file"
                            id="file-upload"
                            onChange={(e) => {
                                if (e.target.files && e.target.files[0]) {
                                    setFile(e.target.files[0]);
                                    setFinancialData([{revenue: '', expenses: ''}, {revenue: '', expenses: ''}]);
                                }
                            }}
                            style={{width: '100%', padding: '0.5rem'}}
                        />
                    </div>
                )}                
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
                    {isLoading ? 'Анализ данных...' : 'Проанализировать данные'}
                </button>
            </form>            
            {analysis && (
                <div className="analysis-result" style={{marginTop: '2rem'}}>
                    <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '1.5rem'}}>
                        <div style={{border: '1px solid #ddd', padding: '1rem', borderRadius: '4px'}}>
                            <h4 style={{margin: '0 0 0.5rem 0'}}>Общий доход</h4>
                            <p style={{fontSize: '1.5rem', fontWeight: 'bold'}}>{analysis.summary.total_revenue.toLocaleString()} ₽</p>
                        </div>
                        <div style={{border: '1px solid #ddd', padding: '1rem', borderRadius: '4px'}}>
                            <h4 style={{margin: '0 0 0.5rem 0'}}>Общие расходы</h4>
                            <p style={{fontSize: '1.5rem', fontWeight: 'bold'}}>{analysis.summary.total_expenses.toLocaleString()} ₽</p>
                        </div>
                        <div style={{border: '1px solid #ddd', padding: '1rem', borderRadius: '4px'}}>
                            <h4 style={{margin: '0 0 0.5rem 0'}}>Прибыль</h4>
                            <p style={{fontSize: '1.5rem', fontWeight: 'bold', color: analysis.summary.profit >= 0 ? 'green' : 'red'}}>
                                {analysis.summary.profit.toLocaleString()} ₽
                            </p>
                        </div>
                        <div style={{border: '1px solid #ddd', padding: '1rem', borderRadius: '4px'}}>
                            <h4 style={{margin: '0 0 0.5rem 0'}}>Рентабельность</h4>
                            <p style={{fontSize: '1.5rem', fontWeight: 'bold'}}>
                                {(analysis.summary.profit_margin * 100).toFixed(2)}%
                            </p>
                        </div>
                    </div>                    
                    <div style={{border: '1px solid #ddd', padding: '1rem', borderRadius: '4px'}}>
                        <h3 style={{marginTop: '0'}}>Подробный анализ:</h3>
                        <div 
                            className="analysis-content" 
                            style={{
                                whiteSpace: 'pre-wrap',
                                lineHeight: '1.6',
                                fontFamily: 'Arial, sans-serif'
                            }}
                        >
                            {analysis.analysis}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default FinancialAnalysisForm;