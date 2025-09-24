import React, { useState, useEffect } from 'react';
import axios from 'axios';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { colors } from '../theme';

function PresentationForm() {
    const [topic, setTopic] = useState<string>('');
    const [audience, setAudience] = useState<string>('общая аудитория');
    const [duration, setDuration] = useState<string>('30 минут');
    const [style, setStyle] = useState<string>('профессиональный');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [presentation, setPresentation] = useState<any>(null);
    const [slides, setSlides] = useState<any[]>([]);
    const sessionToken = localStorage.getItem('session_token');
    useEffect(() => {
        if (presentation) {
            parsePresentationToSlides(presentation.presentation);
        }
    }, [presentation]);
    const parsePresentationToSlides = (presentationText: string) => {
        const slideRegex = /## СЛАЙД \d+: ([^\n]+)/g;
        let match;
        const extractedSlides = [];
        while ((match = slideRegex.exec(presentationText)) !== null) {
            const slideTitle = match[1];
            const slideContent = extractSlideContent(presentationText, slideTitle);
            extractedSlides.push({
                title: slideTitle,
                content: slideContent.content,
                visual: slideContent.visual,
                notes: slideContent.notes
            });
        }
        setSlides(extractedSlides);
    };
    const extractSlideContent = (text: string, slideTitle: string) => {
        const contentRegex = new RegExp(`## СЛАЙД \\d+: ${slideTitle}\\n- Заголовок слайда: [^\\n]+\\n- Содержание: ([^\\n]+)`);
        const visualRegex = /- Визуальные рекомендации: ([^\n]+)/;
        const notesRegex = /- Заметки докладчика: ([\s\S]*?)(?=\n## СЛАЙД|\n## ЗАКЛЮЧЕНИЕ|$)/;
        const contentMatch = text.match(contentRegex);
        const visualMatch = text.match(visualRegex);
        const notesMatch = text.match(notesRegex);        
        return {
            content: contentMatch ? contentMatch[1] : '',
            visual: visualMatch ? visualMatch[1] : '',
            notes: notesMatch ? notesMatch[1].trim() : ''
        };
    };
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!topic.trim()) {
            setError('Пожалуйста, укажите тему презентации');
            return;
        }
        setIsLoading(true);
        setError(null);
        try {
            const response = await axios.post(
                'https://advice-project.onrender.com/generate-presentation/',
                { 
                    topic,
                    audience,
                    duration,
                    style
                },
                { 
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': sessionToken ? `Bearer ${sessionToken}` : ''
                    },
                    timeout: 60000
                }
            );
            setPresentation(response.data);
        } catch (err: any) {
            console.error('Ошибка генерации презентации:', err);
            if (err.response) {
                setError(`Ошибка ${err.response.status}: ${err.response.data.error || 'Не удалось сгенерировать презентацию'}`);
            } else if (err.request) {
                setError('Нет ответа от сервера. Проверьте подключение к интернету.');
            } else {
                setError('Произошла ошибка при отправке запроса.');
            }
        } finally {
            setIsLoading(false);
        }
    };
    const saveAsPDF = () => {
        if (!presentation) return;
        const presentationContent = document.getElementById('presentation-content');
        if (!presentationContent) return;
        html2canvas(presentationContent, {
            scale: 2,
            useCORS: true,
            logging: false
        }).then(canvas => {
            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF({
                orientation: 'portrait',
                unit: 'mm',
                format: 'a4'
            });
            const imgWidth = 210; // A4 width in mm
            const pageHeight = 297; // A4 height in mm
            const imgHeight = canvas.height * imgWidth / canvas.width;
            let heightLeft = imgHeight;
            let position = 0;
            pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
            heightLeft -= pageHeight;
            while (heightLeft >= 0) {
                position = heightLeft - imgHeight;
                pdf.addPage();
                pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
                heightLeft -= pageHeight;
            }
            pdf.save(`презентация-${encodeURIComponent(topic)}.pdf`);
        });
    };
    const saveAsText = () => {
        if (!presentation) return;
        let textContent = `ПРЕЗЕНТАЦИЯ: ${topic}\n\n`;
        slides.forEach((slide, index) => {
            textContent += `СЛАЙД ${index + 1}: ${slide.title}\n`;
            textContent += `Содержание: ${slide.content}\n`;
            textContent += `Визуальные рекомендации: ${slide.visual}\n`;
            textContent += `Заметки докладчика: ${slide.notes}\n\n`;
        });
        const blob = new Blob([textContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `презентация-${encodeURIComponent(topic)}.txt`;
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 0);
    };
    const renderSlidePreview = (slide: any, index: number) => (
        <div key={index} className="slide-preview" style={{
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '8px',
            padding: '1rem',
            marginBottom: '1rem',
            backgroundColor: 'rgba(0, 0, 0, 0.1)'
        }}>
            <h4 style={{
                color: colors.primary,
                marginBottom: '0.5rem'
            }}>
                Слайд {index + 1}: {slide.title}
            </h4>
            <div style={{marginBottom: '0.5rem'}}>
                <strong>Содержание:</strong> {slide.content}
            </div>
            <div style={{marginBottom: '0.5rem'}}>
                <strong>Визуальные рекомендации:</strong> {slide.visual}
            </div>
            <div>
                <strong>Заметки докладчика:</strong> {slide.notes}
            </div>
        </div>
    );
    return (
        <div style={{
            maxWidth: '800px',
            margin: '2rem auto',
            padding: '2rem',
            backgroundColor: 'rgba(255, 255, 255, 0.07)',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.15)'
        }}>
            <h2 style={{
                fontSize: '2rem',
                marginBottom: '1.5rem',
                color: colors.primary,
                textAlign: 'center'
            }}>
                Генерация презентаций
            </h2>
            <p style={{
                color: colors.textSecondary,
                marginBottom: '1.5rem',
                textAlign: 'center',
                lineHeight: '1.6'
            }}>
                Создайте профессиональную презентацию за несколько минут с помощью Советницы АКВИ
            </p>
            {error && (
                <div style={{
                    backgroundColor: 'rgba(255, 99, 71, 0.1)',
                    color: '#ff6347',
                    padding: '1rem',
                    borderRadius: '8px',
                    marginBottom: '1.5rem'
                }}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit} style={{marginBottom: '2rem'}}>
                <div style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="topic" style={{
                        display: 'block',
                        marginBottom: '0.5rem',
                        color: '#f8f8f0',
                        fontWeight: '500'
                    }}>
                        Тема презентации
                    </label>
                    <input
                        type="text"
                        id="topic"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        placeholder="Введите тему презентации"
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
                </div>
                <div style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="audience" style={{
                        display: 'block',
                        marginBottom: '0.5rem',
                        color: '#f8f8f0',
                        fontWeight: '500'
                    }}>
                        Целевая аудитория
                    </label>
                    <select
                        id="audience"
                        value={audience}
                        onChange={(e) => setAudience(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '0.75rem',
                            fontSize: '1rem',
                            borderRadius: '8px',
                            border: '1px solid rgba(255, 255, 255, 0.2)',
                            backgroundColor: 'rgba(0, 0, 0, 0.1)',
                            color: '#f8f8f0'
                        }}
                    >
                        <option value="общая аудитория">Общая аудитория</option>
                        <option value="специалисты">Специалисты</option>
                        <option value="руководители">Руководители</option>
                        <option value="инвесторы">Инвесторы</option>
                        <option value="студенты">Студенты</option>
                    </select>
                </div>
                <div style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="duration" style={{
                        display: 'block',
                        marginBottom: '0.5rem',
                        color: '#f8f8f0',
                        fontWeight: '500'
                    }}>
                        Продолжительность
                    </label>
                    <select
                        id="duration"
                        value={duration}
                        onChange={(e) => setDuration(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '0.75rem',
                            fontSize: '1rem',
                            borderRadius: '8px',
                            border: '1px solid rgba(255, 255, 255, 0.2)',
                            backgroundColor: 'rgba(0, 0, 0, 0.1)',
                            color: '#f8f8f0'
                        }}
                    >
                        <option value="10 минут">10 минут (5-7 слайдов)</option>
                        <option value="20 минут">20 минут (10-12 слайдов)</option>
                        <option value="30 минут">30 минут (15-18 слайдов)</option>
                        <option value="45 минут">45 минут (20-25 слайдов)</option>
                        <option value="60 минут">60 минут (25-30 слайдов)</option>
                    </select>
                </div>
                <div style={{marginBottom: '1.5rem'}}>
                    <label htmlFor="style" style={{
                        display: 'block',
                        marginBottom: '0.5rem',
                        color: '#f8f8f0',
                        fontWeight: '500'
                    }}>
                        Стиль презентации
                    </label>
                    <select
                        id="style"
                        value={style}
                        onChange={(e) => setStyle(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '0.75rem',
                            fontSize: '1rem',
                            borderRadius: '8px',
                            border: '1px solid rgba(255, 255, 255, 0.2)',
                            backgroundColor: 'rgba(0, 0, 0, 0.1)',
                            color: '#f8f8f0'
                        }}
                    >
                        <option value="профессиональный">Профессиональный</option>
                        <option value="академический">Академический</option>
                        <option value="креативный">Креативный</option>
                        <option value="минималистичный">Минималистичный</option>
                        <option value="интерактивный">Интерактивный</option>
                    </select>
                </div>
                <button
                    type="submit"
                    disabled={isLoading || !topic.trim()}
                    style={{
                        backgroundColor: isLoading ? '#cccccc' : colors.primary,
                        color: 'white',
                        border: 'none',
                        padding: '0.85rem 2.5rem',
                        fontSize: '1.1rem',
                        borderRadius: '8px',
                        cursor: isLoading ? 'not-allowed' : 'pointer',
                        fontWeight: 'bold',
                        width: '100',
                        boxShadow: isLoading ? 'none' : '0 4px 15px rgba(122, 106, 200, 0.3)'
                    }}
                >
                    {isLoading ? 'Генерация презентации...' : 'Создать презентацию'}
                </button>
            </form>
            {presentation && (
                <div id="presentation-content" style={{marginTop: '2rem'}}>
                    <h3 style={{
                        fontSize: '1.5rem',
                        marginBottom: '1rem',
                        color: colors.primary
                    }}>
                        Ваша презентация: {topic}
                    </h3>
                    <div style={{
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        borderRadius: '10px',
                        padding: '1.5rem',
                        marginBottom: '1.5rem'
                    }}>
                        <h4 style={{
                            fontSize: '1.2rem',
                            marginBottom: '1rem',
                            color: colors.secondary
                        }}>
                            Целевая аудитория: {audience}
                        </h4>
                        <h4 style={{
                            fontSize: '1.2rem',
                            marginBottom: '1rem',
                            color: colors.secondary
                        }}>
                            Продолжительность: {duration}
                        </h4>
                        <h4 style={{
                            fontSize: '1.2rem',
                            marginBottom: '1rem',
                            color: colors.secondary
                        }}>
                            Стиль: {style}
                        </h4>
                    </div>
                    <h4 style={{
                        fontSize: '1.3rem',
                        marginBottom: '1rem',
                        color: colors.primary
                    }}>
                        Структура презентации
                    </h4>
                    {slides.length > 0 ? (
                        <div>
                            {slides.map(renderSlidePreview)}
                            <div style={{
                                display: 'flex',
                                justifyContent: 'center',
                                gap: '1rem',
                                marginTop: '2rem',
                                flexWrap: 'wrap'
                            }}>
                                <button
                                    onClick={saveAsPDF}
                                    style={{
                                        backgroundColor: colors.primary,
                                        color: 'white',
                                        border: 'none',
                                        padding: '0.75rem 1.5rem',
                                        borderRadius: '8px',
                                        cursor: 'pointer',
                                        fontWeight: 'bold'
                                    }}
                                >
                                    Скачать как PDF
                                </button>
                                <button
                                    onClick={saveAsText}
                                    style={{
                                        backgroundColor: colors.secondary,
                                        color: 'white',
                                        border: 'none',
                                        padding: '0.75rem 1.5rem',
                                        borderRadius: '8px',
                                        cursor: 'pointer',
                                        fontWeight: 'bold'
                                    }}
                                >
                                    Экспорт в текст
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div style={{
                            backgroundColor: 'rgba(255, 165, 0, 0.1)',
                            borderLeft: '4px solid #ffa500',
                            padding: '1rem',
                            borderRadius: '0 5px 5px 0',
                            color: colors.textSecondary
                        }}>
                            Советница АКВИ анализирует структуру презентации...
                        </div>
                    )}
                </div>
            )}
            <div style={{
                marginTop: '2rem',
                padding: '1.5rem',
                backgroundColor: 'rgba(122, 106, 200, 0.1)',
                borderRadius: '10px'
            }}>
                <h3 style={{
                    fontSize: '1.3rem',
                    marginBottom: '0.5rem',
                    color: colors.primary
                }}>
                    Как работает генерация презентаций
                </h3>
                <ul style={{
                    paddingLeft: '1.5rem',
                    color: colors.textSecondary,
                    lineHeight: '1.6'
                }}>
                    <li>Советница АКВИ анализирует вашу тему и целевую аудиторию</li>
                    <li>Создает структуру презентации с учетом продолжительности</li>
                    <li>Генерирует содержание каждого слайда с рекомендациями по оформлению</li>
                    <li>Предоставляет заметки докладчика для каждого слайда</li>
                    <li>Позволяет сохранить презентацию в удобном формате</li>
                </ul>
            </div>
        </div>
    );
}

export default PresentationForm;