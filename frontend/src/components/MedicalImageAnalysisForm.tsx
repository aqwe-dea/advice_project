import React, { useState } from 'react';
import axios from 'axios';

function MedicalImageAnalysisForm() {
    const [image, setImage] = useState<File | null>(null);
    const [imageType, setImageType] = useState<string>('рентген');
    const [country, setCountry] = useState<string>('Россия');
    const [analysis, setAnalysis] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!image) {
            setError('Пожалуйста, загрузите медицинское изображение');
            return;
        }
        setIsLoading(true);
        setError('');
        try {
            const formData = new FormData();
            formData.append('image', image);
            formData.append('image_type', imageType);
            formData.append('country', country);
            const response = await axios.post(
                'https://advice-project.onrender.com/medical-image-analysis/',
                formData,
                { 
                    headers: { 'Content-Type': 'multipart/form-data' },
                    timeout: 60000
                }
            );
            setAnalysis(response.data);
        } catch (err: any) {
            console.error('Ошибка анализа медицинского изображения:', err);
            if (err.response) {
                setError(`Ошибка ${err.response.status}: ${err.response.data.error || 'Не удалось проанализировать изображение'}`);
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
        <div className="medical-analysis-form">
            <h2>Анализ медицинских изображений</h2>
            <p className="disclaimer" style={{color: '#dc3545', fontStyle: 'italic', marginBottom: '1rem'}}>
                Внимание: Этот анализ не заменяет профессиональную медицинскую консультацию. 
                Результаты должны быть проверены квалифицированным врачом.
            </p>
            {error && (
                <div className="error-message" style={{color: 'red', marginBottom: '1rem'}}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit}>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="image-upload" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Загрузите медицинское изображение
                    </label>
                    <input
                        type="file"
                        id="image-upload"
                        accept="image/png, image/jpeg, .dcm"
                        onChange={(e) => {
                            if (e.target.files && e.target.files[0]) {
                                setImage(e.target.files[0]);
                            }
                        }}
                        style={{width: '100%', padding: '0.5rem'}}
                    />
                    <small style={{color: '#666'}}>Поддерживаются форматы JPG, JPEG, PNG и DICOM</small>
                </div>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="image-type" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Тип изображения
                    </label>
                    <select 
                        id="image-type" 
                        value={imageType} 
                        onChange={(e) => setImageType(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    >
                        <option value="рентген">Рентген</option>
                        <option value="МРТ">МРТ</option>
                        <option value="УЗИ">УЗИ</option>
                        <option value="КТ">КТ</option>
                        <option value="фото кожи">Фото кожи</option>
                        <option value="гистология">Гистология</option>
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
                    {isLoading ? 'Анализ изображения...' : 'Проанализировать изображение'}
                </button>
            </form>
            {analysis && (
                <div className="analysis-result" style={{marginTop: '2rem', border: '1px solid #ddd', padding: '1rem', borderRadius: '4px'}}>
                    <h3 style={{marginTop: '0'}}>Результат анализа:</h3>
                    <div style={{display: 'flex', gap: '1rem', marginBottom: '1rem'}}>
                        <span style={{fontWeight: 'bold'}}>Тип изображения:</span>
                        <span>{analysis.image_type}</span>
                    </div>
                    <div style={{display: 'flex', gap: '1rem', marginBottom: '1.5rem'}}>
                        <span style={{fontWeight: 'bold'}}>Страна:</span>
                        <span>{analysis.country}</span>
                    </div>
                    <div 
                        className="analysis-content" 
                        style={{
                            whiteSpace: 'pre-wrap',
                            lineHeight: '1.6',
                            fontFamily: 'Arial, sans-serif',
                            backgroundColor: '#f8f9fa',
                            padding: '1rem',
                            borderRadius: '4px'
                        }}
                    >
                        {analysis.analysis}
                    </div>
                </div>
            )}
            {image && (
                <div className="image-preview" style={{marginTop: '1.5rem'}}>
                    <h3>Предварительный просмотр:</h3>
                    <img 
                        src={URL.createObjectURL(image)} 
                        alt="Предварительный просмотр медицинского изображения" 
                        style={{maxWidth: '100%', maxHeight: '300px', borderRadius: '4px'}}
                    />
                </div>
            )}
        </div>
    );
}

export default MedicalImageAnalysisForm;