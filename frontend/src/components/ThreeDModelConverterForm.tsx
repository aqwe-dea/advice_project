import React, { useState } from 'react';
import axios from 'axios';

function ThreeDModelConverterForm() {
    const [model, setModel] = useState<File | null>(null);
    const [projectType, setProjectType] = useState<string>('строительный');
    const [country, setCountry] = useState<string>('Россия');
    const [result, setResult] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!model) {
            setError('Пожалуйста, загрузите 3D-модель');
            return;
        }
        setIsLoading(true);
        setError('');
        try {
            const formData = new FormData();
            formData.append('model', model);
            formData.append('project_type', projectType);
            formData.append('country', country);
            const response = await axios.post(
                'https://advice-project.onrender.com/3d-to-project/',
                formData,
                { 
                    headers: { 'Content-Type': 'multipart/form-data' },
                    timeout: 60000
                }
            );
            setResult(response.data);
        } catch (err: any) {
            console.error('Ошибка преобразования 3D-модели:', err);
            if (err.response) {
                setError(`Ошибка ${err.response.status}: ${err.response.data.error || 'Не удалось обработать модель'}`);
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
        <div className="3d-converter-form">
            <h2>Преобразование 3D-моделей в реальные проекты</h2>
            <p>Загрузите 3D-модель, и АКВИ поможет преобразовать её в реальный проект с пошаговым планом реализации.</p>
            {error && (
                <div className="error-message" style={{color: 'red', marginBottom: '1rem'}}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit}>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="model-upload" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Загрузите 3D-модель
                    </label>
                    <input
                        type="file"
                        id="model-upload"
                        accept=".stl,.obj,.fbx,.3ds,.dae,.blend"
                        onChange={(e) => {
                            if (e.target.files && e.target.files[0]) {
                                setModel(e.target.files[0]);
                            }
                        }}
                        style={{width: '100%', padding: '0.5rem'}}
                    />
                    <small style={{color: '#666'}}>Поддерживаются форматы: STL, OBJ, FBX, 3DS, DAE, BLEND</small>
                </div>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="project-type" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Тип проекта
                    </label>
                    <select 
                        id="project-type" 
                        value={projectType} 
                        onChange={(e) => setProjectType(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    >
                        <option value="строительный">Строительный проект</option>
                        <option value="архитектурный">Архитектурный проект</option>
                        <option value="инженерный">Инженерный проект</option>
                        <option value="дизайнерский">Дизайнерский проект</option>
                        <option value="промышленный">Промышленный проект</option>
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
                    {isLoading ? 'Обработка модели...' : 'Преобразовать модель'}
                </button>
            </form>
            {result && (
                <div className="conversion-result" style={{marginTop: '2rem', border: '1px solid #ddd', padding: '1rem', borderRadius: '4px'}}>
                    <h3 style={{marginTop: '0'}}>Результат преобразования:</h3>
                    <div style={{display: 'flex', gap: '1rem', marginBottom: '1rem'}}>
                        <span style={{fontWeight: 'bold'}}>Тип проекта:</span>
                        <span>{result.project_type}</span>
                    </div>
                    <div style={{display: 'flex', gap: '1rem', marginBottom: '1.5rem'}}>
                        <span style={{fontWeight: 'bold'}}>Страна:</span>
                        <span>{result.country}</span>
                    </div>
                    <div 
                        className="conversion-analysis" 
                        style={{
                            whiteSpace: 'pre-wrap',
                            lineHeight: '1.6',
                            fontFamily: 'Arial, sans-serif',
                            backgroundColor: '#f8f9fa',
                            padding: '1rem',
                            borderRadius: '4px'
                        }}
                    >
                        {result.analysis}
                    </div>
                </div>
            )}
            {model && (
                <div className="model-preview" style={{marginTop: '1.5rem'}}>
                    <h3>Загруженная модель:</h3>
                    <div style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
                        <span style={{fontSize: '2rem'}}>📁</span>
                        <div>
                            <p style={{margin: '0'}}>{model.name}</p>
                            <p style={{margin: '0', color: '#666', fontSize: '0.9rem'}}>
                                {(model.size / 1024).toFixed(2)} KB • {model.type || '3D модель'}
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default ThreeDModelConverterForm;