import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { colors } from '../theme';

function ThreeDModelConverterForm() {
  const [modelFile, setModelFile] = useState<File | null>(null);
  const [modelType, setModelType] = useState<'stl' | 'obj' | 'gltf'>('stl');
  const [outputType, setOutputType] = useState<'analysis' | 'project'>('project');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{
    original_model: string;
    analysis: {
      model_type: string;
      components: Array<{
        name: string;
        description: string;
        dimensions: {x: number; y: number; z: number};
        material_recommendations: string[];
      }>;
      complexity: number;
      estimated_print_time: string;
    };
    construction_plan: {
      bill_of_materials: Array<{
        component: string;
        material: string;
        quantity: string;
        estimated_cost: number;
      }>;
      assembly_instructions: Array<{
        step_number: number;
        description: string;
        visual_guide: string | null;
      }>;
      total_estimated_cost: number;
      optimization_suggestions: string[];
    };
    refined_project: string;
    model_type: string;
    output_type: string;
  } | null>(null);
  const sessionToken = localStorage.getItem('session_token');
  const handleModelUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setModelFile(file);
      const extension = file.name.split('.').pop()?.toLowerCase();
      if (extension === 'stl') setModelType('stl');
      else if (extension === 'obj') setModelType('obj');
      else if (extension === 'gltf' || extension === 'glb') setModelType('gltf');
      setError(null);
    }
  };
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!modelFile) {
      setError('Пожалуйста, загрузите 3D модель');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('model_file', modelFile);
      formData.append('model_type', modelType);
      formData.append('output_type', outputType);
      const response = await axios.post(
        'https://advice-project.onrender.com/3d-to-project/',
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
      console.error('Ошибка обработки 3D модели:', err);
      if (err.response) {
        setError(`Ошибка ${err.response.status}: ${err.response.data.error || 'Не удалось обработать 3D модель'}`);
      } else if (err.request) {
        setError('Нет ответа от сервера. Проверьте подключение к интернету.');
      } else {
        setError('Произошла ошибка при отправке запроса.');
      }
    } finally {
      setIsLoading(false);
    }
  };
  const renderComplexityMeter = (complexity: number) => {
    const level = complexity * 10;
    const color = complexity < 0.4 ? '#44aa44' : complexity < 0.7 ? '#ffaa33' : '#ff4444';
    return (
      <div style={{
        width: '100%',
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: '10px',
        overflow: 'hidden',
        height: '20px',
        marginTop: '0.5rem'
      }}>
        <div style={{
          width: `${level * 10}%`,
          backgroundColor: color,
          height: '100%',
          transition: 'width 0.5s ease-in-out'
        }}></div>
        <div style={{
          position: 'absolute',
          top: '5px',
          left: `${level * 10 + 2}%`,
          color: '#f8f8f0',
          fontSize: '0.8rem'
        }}>
          {level.toFixed(1)} / 10
        </div>
      </div>
    );
  };
  const downloadModel = () => {
    if (!result || !modelFile) return;
    const link = document.createElement('a');
    link.href = result.original_model;
    link.download = modelFile.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  const exportProjectToText = () => {
    if (!result) return;
    let textContent = `ТЕХНИЧЕСКИЙ ПРОЕКТ: 3D МОДЕЛЬ\n\n`;
    textContent += `Тип модели: ${result.model_type}\n`;
    textContent += `Тип вывода: ${result.output_type === 'analysis' ? 'Анализ' : 'Технический проект'}\n\n`;
    textContent += `=== АНАЛИЗ МОДЕЛИ ===\n`;
    textContent += `Тип конструкции: ${result.analysis.model_type}\n`;
    textContent += `Сложность: ${(result.analysis.complexity * 100).toFixed(0)}%\n`;
    textContent += `Оценочное время печати: ${result.analysis.estimated_print_time}\n\n`;
    textContent += `Компоненты:\n`;
    result.analysis.components.forEach(component => {
      textContent += `- ${component.name}: ${component.description}\n`;
      textContent += `  Размеры: ${component.dimensions.x}x${component.dimensions.y}x${component.dimensions.z} мм\n`;
      textContent += `  Рекомендуемые материалы: ${component.material_recommendations.join(', ')}\n\n`;
    });
    textContent += `=== СМЕТА МАТЕРИАЛОВ ===\n`;
    result.construction_plan.bill_of_materials.forEach(item => {
      textContent += `- ${item.component} (${item.material}):\n`;
      textContent += `  Количество: ${item.quantity}\n`;
      textContent += `  Стоимость: ${item.estimated_cost.toFixed(2)} руб.\n\n`;
    });
    textContent += `Общая стоимость: ${result.construction_plan.total_estimated_cost.toFixed(2)} руб.\n\n`;
    textContent += `=== ПОШАГОВАЯ ИНСТРУКЦИЯ ===\n`;
    result.construction_plan.assembly_instructions.forEach(step => {
      textContent += `${step.step_number}. ${step.description}\n`;
    });
    textContent += `\n=== РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ ===\n`;
    result.construction_plan.optimization_suggestions.forEach(suggestion => {
      textContent += `- ${suggestion}\n`;
    });
    const blob = new Blob([textContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `3d_project_${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 0);
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
        3D Моделирование
      </h2>
      <p style={{
        color: colors.textSecondary,
        marginBottom: '1.5rem',
        textAlign: 'center',
        lineHeight: '1.6'
      }}>
        Загрузите 3D модель для анализа и получения технического проекта. Советница АКВИ поможет превратить вашу модель в реальный проект.
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
            accept=".stl,.obj,.gltf,.glb"
            onChange={handleModelUpload}
            style={{display: 'none'}}
            id="model-upload"
          />
          <label htmlFor="model-upload" style={{
            cursor: 'pointer',
            display: 'inline-block',
            padding: '0.8rem 1.5rem',
            backgroundColor: colors.primary,
            color: 'white',
            borderRadius: '8px',
            fontWeight: 'bold'
          }}>
            {modelFile ? `Выбрано: ${modelFile.name}` : 'Загрузите 3D модель'}
          </label>
          {modelFile && (
            <div style={{marginTop: '1rem'}}>
              <span style={{
                backgroundColor: 'rgba(122, 106, 200, 0.2)',
                color: '#e8e8d3',
                padding: '0.25rem 0.75rem',
                borderRadius: '12px',
                fontSize: '0.9rem'
              }}>
                Тип модели: {modelType.toUpperCase()}
              </span>
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
              Формат модели
            </label>
            <select
              value={modelType}
              onChange={(e) => setModelType(e.target.value as any)}
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
              <option value="stl">STL</option>
              <option value="obj">OBJ</option>
              <option value="gltf">GLTF/GLB</option>
            </select>
          </div>
          <div>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              color: '#f8f8f0',
              fontWeight: '500'
            }}>
              Тип вывода
            </label>
            <select
              value={outputType}
              onChange={(e) => setOutputType(e.target.value as any)}
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
              <option value="analysis">Анализ модели</option>
              <option value="project">Технический проект</option>
            </select>
          </div>
        </div>
        <button
          type="submit"
          disabled={isLoading || !modelFile}
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
          {isLoading ? 'Обработка модели...' : 'Обработать модель'}
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
            Результат обработки
          </h3>
          <div style={{
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '10px',
            padding: '1.5rem',
            marginBottom: '1.5rem'
          }}>
            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem'}}>
              <div>
                <h4 style={{
                  fontSize: '1.2rem',
                  marginBottom: '0.5rem',
                  color: colors.secondary
                }}>
                  Тип конструкции
                </h4>
                <p style={{color: colors.textSecondary}}>
                  {result.analysis.model_type === 'furniture' ? 'Мебель' : 
                   result.analysis.model_type === 'architecture' ? 'Архитектура' : 'Неизвестно'}
                </p>
              </div>
              <div>
                <h4 style={{
                  fontSize: '1.2rem',
                  marginBottom: '0.5rem',
                  color: colors.secondary
                }}>
                  Сложность
                </h4>
                {renderComplexityMeter(result.analysis.complexity)}
              </div>
            </div>
            <div style={{marginTop: '1rem'}}>
              <h4 style={{
                fontSize: '1.2rem',
                marginBottom: '0.5rem',
                color: colors.secondary
              }}>
                Оценочное время печати
              </h4>
              <p style={{color: colors.textSecondary}}>
                {result.analysis.estimated_print_time}
              </p>
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
              Компоненты модели
            </h4>
            <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem'}}>
              {result.analysis.components.map((component, index) => (
                <div key={index} style={{
                  backgroundColor: 'rgba(0, 0, 0, 0.1)',
                  borderRadius: '8px',
                  padding: '1rem'
                }}>
                  <h5 style={{
                    color: colors.primary,
                    marginBottom: '0.5rem'
                  }}>
                    {component.name}
                  </h5>
                  <p style={{color: colors.textSecondary, marginBottom: '0.5rem'}}>
                    {component.description}
                  </p>
                  <p style={{color: colors.textSecondary, marginBottom: '0.5rem'}}>
                    <strong>Размеры:</strong> {component.dimensions.x}x{component.dimensions.y}x{component.dimensions.z} мм
                  </p>
                  <p style={{color: colors.textSecondary}}>
                    <strong>Материалы:</strong> {component.material_recommendations.join(', ')}
                  </p>
                </div>
              ))}
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
              Смета материалов
            </h4>
            <div style={{overflowX: 'auto'}}>
              <table style={{
                width: '100%',
                borderCollapse: 'separate',
                borderSpacing: '0 0.5rem'
              }}>
                <thead>
                  <tr>
                    <th style={{textAlign: 'left', padding: '0.5rem', color: colors.textSecondary}}>Компонент</th>
                    <th style={{textAlign: 'left', padding: '0.5rem', color: colors.textSecondary}}>Материал</th>
                    <th style={{textAlign: 'left', padding: '0.5rem', color: colors.textSecondary}}>Количество</th>
                    <th style={{textAlign: 'left', padding: '0.5rem', color: colors.textSecondary}}>Стоимость</th>
                  </tr>
                </thead>
                <tbody>
                  {result.construction_plan.bill_of_materials.map((item, index) => (
                    <tr key={index} style={{backgroundColor: 'rgba(0, 0, 0, 0.05)', borderRadius: '4px'}}>
                      <td style={{padding: '0.75rem', color: colors.textSecondary}}>{item.component}</td>
                      <td style={{padding: '0.75rem', color: colors.textSecondary}}>{item.material}</td>
                      <td style={{padding: '0.75rem', color: colors.textSecondary}}>{item.quantity}</td>
                      <td style={{padding: '0.75rem', color: colors.textSecondary}}>{item.estimated_cost.toFixed(2)} руб.</td>
                    </tr>
                  ))}
                  <tr style={{fontWeight: 'bold', backgroundColor: 'rgba(122, 106, 200, 0.1)'}}>
                    <td colSpan={3} style={{padding: '0.75rem', color: colors.textSecondary}}>Общая стоимость</td>
                    <td style={{padding: '0.75rem', color: colors.textSecondary}}>{result.construction_plan.total_estimated_cost.toFixed(2)} руб.</td>
                  </tr>
                </tbody>
              </table>
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
              Пошаговая инструкция
            </h4>
            <ol style={{
              paddingLeft: '1.5rem',
              color: colors.textSecondary,
              lineHeight: '1.6'
            }}>
              {result.construction_plan.assembly_instructions.map((step, index) => (
                <li key={index} style={{marginBottom: '1rem'}}>
                  {step.description}
                </li>
              ))}
            </ol>
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
              Рекомендации Советницы АКВИ
            </h4>
            <div style={{
              textAlign: 'left',
              whiteSpace: 'pre-wrap',
              lineHeight: '1.6'
            }}>
              {result.refined_project}
            </div>
          </div>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '1rem',
            marginTop: '2rem',
            flexWrap: 'wrap'
          }}>
            <button
              onClick={downloadModel}
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
              Скачать исходную модель
            </button>
            <button
              onClick={exportProjectToText}
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
              Экспорт проекта в текст
            </button>
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
          Как работает 3D моделирование
        </h3>
        <ul style={{
          paddingLeft: '1.5rem',
          color: colors.textSecondary,
          lineHeight: '1.6'
        }}>
          <li>Мы анализируем вашу 3D модель и определяем её компоненты и сложность</li>
          <li>Генерируем смету материалов и пошаговую инструкцию по сборке</li>
          <li>Предоставляем рекомендации по оптимизации конструкции и выбору материалов</li>
          <li>Помогаем превратить цифровую модель в реальный проект</li>
        </ul>
        <p style={{marginTop: '1rem', color: colors.textSecondary}}>
          <strong>Примечание:</strong> После 1 октября, когда возобновятся кредиты на Hugging Face, 
          мы сможем интегрировать реальные модели для более точного анализа 3D моделей.
        </p>
      </div>
    </div>
  );
}

export default ThreeDModelConverterForm;