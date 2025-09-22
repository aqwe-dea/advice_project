import React, { useState } from 'react';
import axios from 'axios';
import { colors } from '../theme';

function PhotoRestorationForm() {
  const [image, setImage] = useState<File | null>(null);
  const [repairLevel, setRepairLevel] = useState<'light' | 'medium' | 'heavy' | 'full'>('medium');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{
    restored_image: string;
    analysis: {
      damage_type: string;
      damage_severity: number;
      recommended_method: string;
      description: string;
    };
    restoration_report: string;
  } | null>(null);
  const sessionToken = localStorage.getItem('session_token');
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setImage(e.target.files[0]);
      setError(null);
    }
  };
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!image) {
      setError('Пожалуйста, загрузите изображение');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('image', image);
      formData.append('repair_level', repairLevel);
      const response = await axios.post(
        'https://advice-project.onrender.com/photo-restoration/',
        formData,
        { 
          headers: { 
            'Content-Type': 'multipart/form-data',
            'Authorization': sessionToken ? `Bearer ${sessionToken}` : ''
          },
          timeout: 45000
        }
      );
      setResult(response.data);
    } catch (err: any) {
      console.error('Ошибка реставрации фото:', err);
      if (err.response) {
        setError(`Ошибка ${err.response.status}: ${err.response.data.error || 'Не удалось обработать изображение'}`);
      } else if (err.request) {
        setError('Нет ответа от сервера. Проверьте подключение к интернету.');
      } else {
        setError('Произошла ошибка при отправке запроса.');
      }
    } finally {
      setIsLoading(false);
    }
  };
  const downloadRestoredImage = () => {
    if (!result) return;
    const link = document.createElement('a');
    link.href = result.restored_image;
    link.download = `restored_${new Date().toISOString().slice(0, 10)}.jpg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
            onChange={handleImageUpload}
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
            {image ? `Выбрано: ${image.name}` : 'Выберите изображение'}
          </label>
          {image && (
            <div style={{marginTop: '1rem'}}>
              <img 
                src={URL.createObjectURL(image)} 
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
        <div style={{marginBottom: '1.5rem'}}>
          <label style={{
            display: 'block',
            marginBottom: '0.5rem',
            color: '#f8f8f0',
            fontWeight: '500'
          }}>
            Уровень восстановления
          </label>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '0.5rem'
          }}>
            {['light', 'medium', 'heavy', 'full'].map(level => (
              <button
                key={level}
                type="button"
                onClick={() => setRepairLevel(level as any)}
                style={{
                  backgroundColor: repairLevel === level ? colors.primary : 'rgba(255, 255, 255, 0.1)',
                  color: 'white',
                  border: 'none',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: repairLevel === level ? 'bold' : 'normal'
                }}
              >
                {level === 'light' && 'Легкий'}
                {level === 'medium' && 'Средний'}
                {level === 'heavy' && 'Серьезный'}
                {level === 'full' && 'Полное'}
              </button>
            ))}
          </div>
        </div>
        <button
          type="submit"
          disabled={isLoading || !image}
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
      {result && (
        <div style={{textAlign: 'center'}}>
          <h3 style={{
            fontSize: '1.5rem',
            marginBottom: '1rem',
            color: colors.primary
          }}>
            Результат восстановления
          </h3>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '2rem',
            flexWrap: 'wrap',
            marginBottom: '1.5rem'
          }}>
            <div>
              <h4 style={{color: colors.textSecondary, marginBottom: '0.5rem'}}>Оригинал</h4>
              <img 
                src={URL.createObjectURL(image!)} 
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
                src={result.restored_image} 
                alt="Restored" 
                style={{
                  maxWidth: '300px',
                  borderRadius: '8px',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }} 
              />
            </div>
          </div>
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
              Анализ повреждений
            </h4>
            <div style={{textAlign: 'left', display: 'inline-block'}}>
              <p><strong>Тип повреждений:</strong> {result.analysis.damage_type}</p>
              <p><strong>Степень повреждения:</strong> {(result.analysis.damage_severity * 100).toFixed(0)}%</p>
              <p><strong>Рекомендованный метод:</strong> {result.analysis.recommended_method === 'local' ? 'Локальная обработка' : 'Генерация нового изображения'}</p>
            </div>
          </div>
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
              Отчет о восстановлении
            </h4>
            <div style={{
              textAlign: 'left',
              whiteSpace: 'pre-wrap',
              lineHeight: '1.6'
            }}>
              {result.restoration_report}
            </div>
          </div>
          <button
            onClick={downloadRestoredImage}
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
            Скачать восстановленное изображение
          </button>
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