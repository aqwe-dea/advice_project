import React, { useState } from 'react';
import axios from 'axios';
import { colors } from '../theme';

function MedicalImageAnalysisForm() {
  const [image, setImage] = useState<File | null>(null);
  const [imageType, setImageType] = useState<'x-ray' | 'mri' | 'ultrasound' | 'ct'>('x-ray');
  const [userType, setUserType] = useState<'patient' | 'professional'>('patient');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{
    original_image: string;
    analysis: {
      abnormalities: Array<{
        x: number;
        y: number;
        width: number;
        height: number;
        description: string;
        severity: number;
        confidence: number;
      }>;
      overall_assessment: string;
      recommendations: string[];
    };
    report: string;
    image_type: string;
    user_type: string;
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
      formData.append('image_type', imageType);
      formData.append('user_type', userType);
      const response = await axios.post(
        'https://advice-project.onrender.com/medical-image-analysis/',
        formData,
        { 
          headers: { 
            'Content-Type': 'multipart/form-data',
            'Authorization': sessionToken ? `Bearer ${sessionToken}` : ''
          },
          timeout: 60000
        }
      );
      setResult(response.data);
    } catch (err: any) {
      console.error('Ошибка медицинского анализа:', err);
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
  const renderAbnormalities = (containerWidth: number, containerHeight: number) => {
    if (!result || !result.analysis.abnormalities.length) return null;
    return (
      <div style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%'}}>
        {result.analysis.abnormalities.map((ab, index) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              left: `${ab.x * 100}%`,
              top: `${ab.y * 100}%`,
              width: `${ab.width * 100}%`,
              height: `${ab.height * 100}%`,
              border: `2px solid ${ab.severity > 0.7 ? '#ff4444' : ab.severity > 0.4 ? '#ffaa33' : '#44aa44'}`,
              borderRadius: '4px',
              pointerEvents: 'none',
              boxShadow: `0 0 0 2px rgba(${ab.severity > 0.7 ? '255,68,68' : ab.severity > 0.4 ? '255,170,51' : '68,170,68'}, 0.5)`,
              animation: 'pulse 2s infinite'
            }}
          >
            <div style={{
              position: 'absolute',
              bottom: '-20px',
              left: '50%',
              transform: 'translateX(-50%)',
              backgroundColor: ab.severity > 0.7 ? '#ff4444' : ab.severity > 0.4 ? '#ffaa33' : '#44aa44',
              color: 'white',
              padding: '2px 8px',
              borderRadius: '12px',
              fontSize: '0.8rem',
              whiteSpace: 'nowrap'
            }}>
              {ab.description}
            </div>
          </div>
        ))}
      </div>
    );
  };
  return (
    <div style={{
      maxWidth: '1000px',
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
        Медицинский анализ
      </h2>
      <p style={{
        color: colors.textSecondary,
        marginBottom: '1.5rem',
        textAlign: 'center',
        lineHeight: '1.6'
      }}>
        Загрузите медицинское изображение для анализа. Советница АКВИ предоставит профессиональную интерпретацию результатов.
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
            {image ? `Выбрано: ${image.name}` : 'Загрузите медицинское изображение'}
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
        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem'}}>
          <div>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              color: '#f8f8f0',
              fontWeight: '500'
            }}>
              Тип изображения
            </label>
            <select
              value={imageType}
              onChange={(e) => setImageType(e.target.value as any)}
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
              <option value="x-ray">Рентген</option>
              <option value="mri">МРТ</option>
              <option value="ultrasound">УЗИ</option>
              <option value="ct">КТ</option>
            </select>
          </div>
          <div>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              color: '#f8f8f0',
              fontWeight: '500'
            }}>
              Тип пользователя
            </label>
            <select
              value={userType}
              onChange={(e) => setUserType(e.target.value as any)}
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
              <option value="patient">Пациент</option>
              <option value="professional">Профессионал</option>
            </select>
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
          {isLoading ? 'Анализ изображения...' : 'Проанализировать изображение'}
        </button>
      </form>
      {result && (
        <div>
          <h3 style={{
            fontSize: '1.5rem',
            marginBottom: '1rem',
            color: colors.primary,
            textAlign: 'center'
          }}>
            Результат анализа
          </h3>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '2rem',
            flexWrap: 'wrap',
            marginBottom: '1.5rem'
          }}>
            <div style={{position: 'relative', maxWidth: '500px'}}>
              <h4 style={{color: colors.textSecondary, marginBottom: '0.5rem', textAlign: 'center'}}>
                Медицинское изображение
              </h4>
              <div style={{position: 'relative', display: 'inline-block'}}>
                <img 
                  src={result.original_image} 
                  alt="Medical" 
                  style={{
                    maxWidth: '100%',
                    borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }} 
                />
                {renderAbnormalities(500, 500)}
              </div>
              {result.analysis.abnormalities.length > 0 && (
                <div style={{
                  display: 'flex',
                  justifyContent: 'center',
                  gap: '1rem',
                  marginTop: '1rem',
                  flexWrap: 'wrap'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <span style={{
                      display: 'inline-block',
                      width: '16px',
                      height: '16px',
                      backgroundColor: 'rgba(68, 170, 68, 0.5)',
                      border: '1px solid #44aa44'
                    }}></span>
                    <span>Низкий риск</span>
                  </div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <span style={{
                      display: 'inline-block',
                      width: '16px',
                      height: '16px',
                      backgroundColor: 'rgba(255, 170, 51, 0.5)',
                      border: '1px solid #ffaa33'
                    }}></span>
                    <span>Средний риск</span>
                  </div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <span style={{
                      display: 'inline-block',
                      width: '16px',
                      height: '16px',
                      backgroundColor: 'rgba(255, 68, 68, 0.5)',
                      border: '1px solid #ff4444'
                    }}></span>
                    <span>Высокий риск</span>
                  </div>
                </div>
              )}
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
              {userType === 'patient' ? 'Рекомендации для пациента' : 'Профессиональный отчет'}
            </h4>
            <div style={{
              textAlign: 'left',
              whiteSpace: 'pre-wrap',
              lineHeight: '1.6'
            }}>
              {result.report}
            </div>
          </div>
          {result.analysis.abnormalities.length > 0 && (
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
                Выявленные аномалии
              </h4>
              <div style={{textAlign: 'left'}}>
                {result.analysis.abnormalities.map((ab, index) => (
                  <div key={index} style={{marginBottom: '1rem'}}>
                    <p><strong>Описание:</strong> {ab.description}</p>
                    <p><strong>Уровень серьезности:</strong> {(ab.severity * 100).toFixed(0)}%</p>
                    <p><strong>Уверенность:</strong> {(ab.confidence * 100).toFixed(0)}%</p>
                  </div>
                ))}
              </div>
            </div>
          )}
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
              Рекомендации
            </h4>
            <ul style={{
              paddingLeft: '1.5rem',
              lineHeight: '1.6'
            }}>
              {result.analysis.recommendations.map((rec, index) => (
                <li key={index} style={{marginBottom: '0.5rem'}}>{rec}</li>
              ))}
            </ul>
          </div>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '1rem',
            marginTop: '2rem',
            flexWrap: 'wrap'
          }}>
            <button
              onClick={() => {
                const blob = new Blob([result.report], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `medical_report_${new Date().toISOString().slice(0, 10)}.txt`;
                document.body.appendChild(a);
                a.click();
                setTimeout(() => {
                  document.body.removeChild(a);
                  URL.revokeObjectURL(url);
                }, 0);
              }}
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
              Скачать отчет
            </button>
            {userType === 'professional' && (
              <button
                onClick={() => {
                  alert('Функция генерации PDF будет доступна после 1 октября');
                }}
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
                Экспорт в PDF
              </button>
            )}
          </div>
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
          Как работает медицинский анализ
        </h3>
        <ul style={{
          paddingLeft: '1.5rem',
          color: colors.textSecondary,
          lineHeight: '1.6'
        }}>
          <li>Мы анализируем ваше медицинское изображение с использованием передовых моделей ИИ</li>
          <li>Выявляем потенциальные аномалии и области, требующие внимания</li>
          <li>Генерируем отчет, адаптированный под ваш уровень знаний</li>
          <li>Предоставляем рекомендации по дальнейшим действиям</li>
          <li>Выделяем на изображении области интереса для удобства анализа</li>
        </ul>
        <p style={{marginTop: '1rem', color: colors.textSecondary}}>
          <strong>Важно:</strong> Результаты, полученные с помощью Советницы АКВИ, не заменяют профессиональную медицинскую консультацию. 
          Всегда консультируйтесь с квалифицированным врачом для постановки диагноза и назначения лечения.
        </p>
      </div>
    </div>
  );
}

export default MedicalImageAnalysisForm;