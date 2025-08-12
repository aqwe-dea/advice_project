import React, { useState } from 'react';
import axios from 'axios';

function PhotoRestorationForm() {
    const [photo, setPhoto] = useState<File | null>(null);
    const [enhancementLevel, setEnhancementLevel] = useState<string>('стандартное');
    const [result, setResult] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!photo) {
            setError('Пожалуйста, загрузите фотографию');
            return;
        }
        setIsLoading(true);
        setError('');
        try {
            const formData = new FormData();
            formData.append('photo', photo);
            formData.append('enhancement_level', enhancementLevel);
            const response = await axios.post(
                'https://advice-project.onrender.com/photo-restoration/',
                formData,
                { 
                    headers: { 'Content-Type': 'multipart/form-data' },
                    timeout: 60000
                }
            );
            setResult(response.data);
        } catch (err: any) {
            console.error('Ошибка реставрации фото:', err);
            if (err.response) {
                setError(`Ошибка ${err.response.status}: ${err.response.data.error || 'Не удалось обработать фото'}`);
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
        <div className="photo-restoration-form">
            <h2>Реставрация старых фотографий</h2>
            <p>Загрузите старое или поврежденное фото, и АКВИ поможет его восстановить и улучшить.</p>
            {error && (
                <div className="error-message" style={{color: 'red', marginBottom: '1rem'}}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit}>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="photo-upload" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Загрузите фотографию
                    </label>
                    <input
                        type="file"
                        id="photo-upload"
                        accept="image/png, image/jpeg"
                        onChange={(e) => {
                            if (e.target.files && e.target.files[0]) {
                                setPhoto(e.target.files[0]);
                            }
                        }}
                        style={{width: '100%', padding: '0.5rem'}}
                    />
                    <small style={{color: '#666'}}>Поддерживаются форматы JPG, JPEG и PNG</small>
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="enhancement" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Уровень улучшения
                    </label>
                    <select 
                        id="enhancement" 
                        value={enhancementLevel} 
                        onChange={(e) => setEnhancementLevel(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    >
                        <option value="стандартное">Стандартное восстановление</option>
                        <option value="детальное">Детальное восстановление</option>
                        <option value="цветизация">Цветизация черно-белого фото</option>
                        <option value="профессиональное">Профессиональное улучшение</option>
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
                    {isLoading ? 'Обработка фото...' : 'Восстановить фото'}
                </button>
            </form>
            {result && (
                <div className="restoration-result" style={{marginTop: '2rem', border: '1px solid #ddd', padding: '1rem', borderRadius: '4px'}}>
                    <h3 style={{marginTop: '0'}}>Результат реставрации:</h3>
                    <div 
                        className="restoration-description" 
                        style={{
                            whiteSpace: 'pre-wrap',
                            lineHeight: '1.6',
                            fontFamily: 'Arial, sans-serif',
                            backgroundColor: '#f8f9fa',
                            padding: '1rem',
                            borderRadius: '4px'
                        }}
                    >
                        {result.restoration_description}
                    </div>
                    <div style={{marginTop: '1rem', fontStyle: 'italic', color: '#666'}}>
                        Уровень улучшения: {result.enhancement_level}
                    </div>
                </div>
            )}
            {photo && (
                <div className="photo-preview" style={{marginTop: '1.5rem'}}>
                    <h3>Предварительный просмотр:</h3>
                    <img 
                        src={URL.createObjectURL(photo)} 
                        alt="Предварительный просмотр" 
                        style={{maxWidth: '100%', maxHeight: '300px', borderRadius: '4px'}}
                    />
                </div>
            )}
        </div>
    );
}

export default PhotoRestorationForm;