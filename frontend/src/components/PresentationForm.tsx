import React, { useState } from 'react';
import axios from 'axios';

function PresentationForm() {
    const [topic, setTopic] = useState<string>('');
    const [presentationType, setPresentationType] = useState<string>('бизнес');
    const [slidesCount, setSlidesCount] = useState<number>(10);
    const [presentation, setPresentation] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!topic.trim()) {
            setError('Пожалуйста, укажите тему презентации');
            return;
        }
        setIsLoading(true);
        setError('');
        try {
            const response = await axios.post(
                'https://advice-project.onrender.com/generate-presentation/',
                { 
                    topic, 
                    type: presentationType, 
                    slides_count: slidesCount 
                },
                { 
                    headers: { 'Content-Type': 'application/json' },
                    timeout: 60000
                }
            );
            setPresentation(response.data);
        } catch (err: any) {
            console.error('Ошибка генерации презентации:', err);
            if (err.response) {
                const reader = new FileReader();
                reader.onload = () => {
                    try {
                        const errorData = JSON.parse(reader.result as string);
                        setError(`Ошибка ${err.response.status}: ${errorData.error || 'Не удалось сгенерировать презентацию'}`);
                    } catch (e) {
                        setError(`Ошибка ${err.response.status}: Не удалось сгенерировать презентацию`);
                    }
                };
                reader.readAsText(err.response.data);
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
        <div className="presentation-form">
            <h2>Генерация презентаций</h2>
            <p>Введите тему, и АКВИ создаст профессиональную структуру презентации в удобном формате.</p>
            {error && (
                <div className="error-message" style={{color: 'red', marginBottom: '1rem'}}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit}>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="topic" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Тема презентации
                    </label>
                    <input
                        type="text"
                        id="topic"
                        placeholder="Введите тему презентации"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    />
                </div>
                <div className="form-group" style={{marginBottom: '1rem'}}>
                    <label htmlFor="presentation-type" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Тип презентации
                    </label>
                    <select 
                        id="presentation-type" 
                        value={presentationType} 
                        onChange={(e) => setPresentationType(e.target.value)}
                        style={{width: '100%', padding: '0.5rem', fontSize: '1rem'}}
                    >
                        <option value="бизнес">Бизнес-презентация</option>
                        <option value="образовательная">Образовательная презентация</option>
                        <option value="научная">Научная презентация</option>
                        <option value="продажи">Презентация для продаж</option>
                        <option value="инвестиционная">Инвестиционный меморандум</option>
                    </select>
                </div>
                <div className="form-group" style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="slides-count" style={{display: 'block', marginBottom: '0.5rem'}}>
                        Количество слайдов (5-20)
                    </label>
                    <input
                        type="range"
                        id="slides-count"
                        min="5"
                        max="20"
                        value={slidesCount}
                        onChange={(e) => setSlidesCount(parseInt(e.target.value))}
                        style={{width: '100%'}}
                    />
                    <div style={{textAlign: 'center', marginTop: '0.5rem'}}>{slidesCount} слайдов</div>
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
                    {isLoading ? 'Генерация презентации...' : 'Создать структуру'}
                </button>
            </form>
            {presentation && (
                <div className="presentation-result" style={{marginTop: '2rem', border: '1px solid #ddd', padding: '1rem', borderRadius: '4px'}}>
                    <h3 style={{marginTop: '0'}}>{presentation.title || 'Структура презентации'}</h3>
                    {presentation.slides && presentation.slides.map((slide: any, index: number) => (
                        <div key={index} style={{border: '1px solid #eee', borderRadius: '4px', padding: '1rem', marginBottom: '1rem'}}>
                            <h4 style={{marginTop: '0'}}>Слайд {index + 1}: {slide.title}</h4>
                            <p><strong>Содержание:</strong> {slide.content}</p>
                            {slide.notes && (
                                <p><strong>Заметки докладчика:</strong> {slide.notes}</p>
                            )}
                        </div>
                    ))}
                    <div style={{marginTop: '1.5rem', backgroundColor: '#f8f9fa', padding: '1rem', borderRadius: '4px'}}>
                        <p>Вы можете скопировать эту структуру и использовать её для создания слайдов в PowerPoint, Google Slides или другом инструменте.</p>
                    </div>
                </div>
            )}
        </div>
    );
}

export default PresentationForm;