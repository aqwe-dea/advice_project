import React, { useState } from 'react';
import axios from 'axios';

function LegalDocumentAnalysisForm() {
    const [document, setDocument] = useState<string>('');
    const [country, setCountry] = useState<string>('Россия');
    const [analysis, setAnalysis] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const [file, setFile] = useState<File | null>(null);
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!document && !file) {
            setError('Пожалуйста, укажите документ или загрузите файл');
            return;
        }
        setIsLoading(true);
        setError('');
        try {
            const formData = new FormData();
            if (file) {
                formData.append('document', file);
                formData.append('country', country);
            } else {
                formData.append('document', document);
                formData.append('country', country);
            }
            const response = await axios.post(
                'https://advice-project.onrender.com/legal-document-analysis/',
                file ? formData : { document, country },
                { 
                    headers: { 
                        'Content-Type': file ? 'multipart/form-data' : 'application/json'
                    },
                    timeout: 30000
                }
            );
            if (response.data.analysis) {
                setAnalysis(response.data.analysis);
            } else {
                setError('Сервер вернул пустой ответ. Попробуйте другой документ.');
            }
        } catch (err: any) {
            console.error('Ошибка юридического анализа:', err);
            if (err.response) {
                setError(`Ошибка ${err.response.status}: ${err.response.data.error || 'Не удалось проанализировать документ'}`);
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
        <div className="legal-analysis-form">
            <h2>Юридический анализ документов</h2>
            <p>Загрузите документ или введите его текст для проверки на соответствие законодательству выбранной страны.</p>      
            {error && (
                <div className="error-message" style={{color: 'red', marginBottom: '1rem'}}>
                    {error}
                </div>
            )}            
            <form onSubmit={handleSubmit}>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="document-type" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Тип ввода
                    </label>
                    <select 
                        id="document-type" 
                        onChange={(e) => {
                            if (e.target.value === 'text') {
                                setFile(null);
                            } else {
                                setDocument('');
                            }
                        }}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    >
                        <option value="text">Текстовый ввод</option>
                        <option value="file">Загрузка файла</option>
                    </select>
                </div>                
                {document && (
                    <div className="form-group" style={{marginBottom: '1rem'}}>
                        <label htmlFor="document" style={{display: 'block', marginBottom: '0.5rem'}}>
                            Текст документа
                        </label>
                        <textarea
                            id="document"
                            placeholder="Введите текст юридического документа"
                            value={document}
                            onChange={(e) => setDocument(e.target.value)}
                            style={{width: '100%', height: '200px', padding: '0.5rem', fontSize: '1rem'}}
                            disabled={file !== null}
                        />
                    </div>
                )}                
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
                {!document && !file && (
                    <div className="form-group" style={{marginBottom: '1rem'}}>
                        <label htmlFor="file-upload" style={{display: 'block', marginBottom: '0.5rem'}}>
                            Загрузите документ
                        </label>
                        <input
                            type="file"
                            id="file-upload"
                            onChange={(e) => {
                                if (e.target.files && e.target.files[0]) {
                                    setFile(e.target.files[0]);
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
                    {isLoading ? 'Анализ документа...' : 'Проанализировать документ'}
                </button>
            </form>            
            {analysis && (
                <div className="analysis-result" style={{marginTop: '2rem', border: '1px solid #ddd', padding: '1rem', borderRadius: '4px'}}>
                    <h3 style={{marginTop: '0'}}>Результат анализа:</h3>
                    <div 
                        className="analysis-content" 
                        style={{
                            whiteSpace: 'pre-wrap',
                            lineHeight: '1.6',
                            fontFamily: 'Arial, sans-serif'
                        }}
                    >
                        {analysis}
                    </div>
                </div>
            )}
        </div>
    );
}

export default LegalDocumentAnalysisForm;