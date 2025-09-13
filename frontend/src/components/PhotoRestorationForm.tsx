import React, { useState } from 'react';
import axios from 'axios';
import { colors } from '../theme';

function PhotoRestorationForm() {
    const [imageFile, setImageFile] = useState<File | null>(null);
    const [restoredImage, setRestoredImage] = useState<string | null>(null);
    const [analysis, setAnalysis] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setImageFile(e.target.files[0]);
            setError(null);
        }
    };
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!imageFile) {
            setError('Пожалуйста, загрузите изображение');
            return;
        }
        setIsLoading(true);
        setError(null);
        try {
            const formData = new FormData();
            formData.append('image', imageFile);
            const response = await axios.post(
                'https://advice-project.onrender.com/photo-restoration/',
                formData,
                { 
                    headers: { 
                        'Content-Type': 'multipart/form-data',
                        'Authorization': `Bearer ${localStorage.getItem('session_token')}`
                    },
                    timeout: 60000
                }
            );
            if (response.data.restored_image) {
                setRestoredImage(response.data.restored_image);
            }
            if (response.data.analysis) {
                setAnalysis(response.data.analysis);
            }
        } catch (err: any) {
            console.error('Ошибка реставрации фото:', err);
            setError(err.response?.data?.error || 'Не удалось обработать изображение');
        } finally {
            setIsLoading(false);
        }
    };
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
                Реставрация фотографий
            </h2>
            <p style={{
                color: colors.textSecondary,
                marginBottom: '1.5rem',
                textAlign: 'center',
                lineHeight: '1.6'
            }}>
                Загрузите поврежденное изображение, и Советница АКВИ выполнит его профессиональную реставрацию
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
                <div style={{
                    border: '2px dashed rgba(255, 255, 255, 0.2)',
                    borderRadius: '12px',
                    padding: '2rem',
                    textAlign: 'center',
                    backgroundColor: 'rgba(0, 0, 0, 0.1)',
                    marginBottom: '1.5rem'
                }}>
                    <input
                        type="file"
                        accept="image/*"
                        onChange={handleFileChange}
                        style={{display: 'none'}}
                        id="image-upload"
                    />
                    <label htmlFor="image-upload" style={{
                        cursor: 'pointer',
                        display: 'inline-block',
                        padding: '0.8rem 1.5rem',
                        backgroundColor: colors.primary,
                        color: 'white',
                        borderRadius: '8px',
                        fontWeight: 'bold'
                    }}>
                        {imageFile ? `Выбрано: ${imageFile.name}` : 'Выберите изображение'}
                    </label>
                    {imageFile && (
                        <div style={{marginTop: '1rem'}}>
                            <img 
                                src={URL.createObjectURL(imageFile)} 
                                alt="Preview" 
                                style={{
                                    maxWidth: '100%',
                                    maxHeight: '200px',
                                    borderRadius: '8px'
                                }} 
                            />
                        </div>
                    )}
                </div>
                <button
                    type="submit"
                    disabled={isLoading || !imageFile}
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
                    {isLoading ? 'Восстановление фото...' : 'Восстановить фото'}
                </button>
            </form>
            {analysis && (
                <div style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    borderRadius: '10px',
                    padding: '1.5rem',
                    marginBottom: '2rem'
                }}>
                    <h3 style={{
                        fontSize: '1.5rem',
                        marginBottom: '1rem',
                        color: colors.primary
                    }}>
                        Анализ повреждений
                    </h3>
                    <div style={{
                        backgroundColor: 'rgba(0, 0, 0, 0.2)',
                        borderRadius: '8px',
                        padding: '1rem',
                        color: colors.textSecondary,
                        whiteSpace: 'pre-wrap'
                    }}>
                        {analysis}
                    </div>
                </div>
            )}
            {restoredImage && (
                <div style={{textAlign: 'center'}}>
                    <h3 style={{
                        fontSize: '1.5rem',
                        marginBottom: '1rem',
                        color: colors.primary
                    }}>
                        Восстановленное изображение
                    </h3>
                    <div style={{
                        display: 'flex',
                        justifyContent: 'center',
                        gap: '2rem',
                        flexWrap: 'wrap'
                    }}>
                        <div>
                            <h4 style={{color: colors.textSecondary, marginBottom: '0.5rem'}}>Оригинал</h4>
                            <img 
                                src={URL.createObjectURL(imageFile!)} 
                                alt="Original" 
                                style={{
                                    maxWidth: '300px',
                                    borderRadius: '8px',
                                    border: '1px solid rgba(255, 255, 255, 0.1)'
                                }} 
                            />
                        </div>
                        <div>
                            <h4 style={{color: colors.textSecondary, marginBottom: '0.5rem'}}>Восстановлено</h4>
                            <img 
                                src={restoredImage} 
                                alt="Restored" 
                                style={{
                                    maxWidth: '300px',
                                    borderRadius: '8px',
                                    border: '1px solid rgba(255, 255, 255, 0.1)'
                                }} 
                            />
                        </div>
                    </div>
                    <a 
                        href={restoredImage} 
                        download="restored_photo.jpg"
                        style={{
                            display: 'inline-block',
                            marginTop: '1.5rem',
                            backgroundColor: colors.secondary,
                            color: 'white',
                            padding: '0.75rem 1.5rem',
                            borderRadius: '8px',
                            textDecoration: 'none',
                            fontWeight: 'bold'
                        }}
                    >
                        Скачать восстановленное изображение
                    </a>
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
                    Как работает реставрация
                </h3>
                <ul style={{
                    paddingLeft: '1.5rem',
                    color: colors.textSecondary,
                    lineHeight: '1.6'
                }}>
                    <li>Мы анализируем повреждения на изображении</li>
                    <li>Применяем специализированные алгоритмы для восстановления</li>
                    <li>Улучшаем цвет, резкость и детали</li>
                    <li>Удаляем царапины и другие дефекты</li>
                    <li>Сохраняем оригинальную стилистику изображения</li>
                </ul>
            </div>
        </div>
    );
}

export default PhotoRestorationForm;