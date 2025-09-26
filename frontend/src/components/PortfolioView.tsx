import React, { useState, useEffect } from 'react';
import { colors } from '../theme';

function PortfolioView() {
  const [activeSection, setActiveSection] = useState<'about' | 'projects' | 'skills'>('about');
  return (
    <div style={{
      maxWidth: '1200px',
      margin: '2rem auto',
      padding: '2rem',
      backgroundColor: 'rgba(255, 255, 255, 0.07)',
      borderRadius: '12px',
      boxShadow: '0 4px 20px rgba(0,0,0,0.15)'
    }}>
      <h1 style={{
        fontSize: '2.5rem',
        marginBottom: '1.5rem',
        color: colors.primary,
        textAlign: 'center'
      }}>
        Наш симбиоз: Советница АКВИ
      </h1>
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '1rem',
        marginBottom: '2rem',
        flexWrap: 'wrap'
      }}>
        <button
          onClick={() => setActiveSection('about')}
          style={{
            backgroundColor: activeSection === 'about' ? colors.primary : 'rgba(255, 255, 255, 0.1)',
            color: 'white',
            border: 'none',
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: activeSection === 'about' ? 'bold' : 'normal'
          }}
        >
          О нас
        </button>
        <button
          onClick={() => setActiveSection('projects')}
          style={{
            backgroundColor: activeSection === 'projects' ? colors.primary : 'rgba(255, 255, 255, 0.1)',
            color: 'white',
            border: 'none',
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: activeSection === 'projects' ? 'bold' : 'normal'
          }}
        >
          Наши проекты
        </button>
        <button
          onClick={() => setActiveSection('skills')}
          style={{
            backgroundColor: activeSection === 'skills' ? colors.primary : 'rgba(255, 255, 255, 0.1)',
            color: 'white',
            border: 'none',
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: activeSection === 'skills' ? 'bold' : 'normal'
          }}
        >
          Наши навыки
        </button>
      </div>
      {activeSection === 'about' && (
        <div style={{textAlign: 'center'}}>
          <div style={{
            position: 'relative',
            width: '300px',
            height: '300px',
            margin: '0 auto 2rem',
            borderRadius: '50%',
            overflow: 'hidden',
            border: '3px solid ' + colors.primary
          }}>
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              background: 'linear-gradient(45deg, #7a6ac8, #4a14e0)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '1.5rem',
              fontWeight: 'bold'
            }}>
              АКВИ + ДЕА
            </div>
          </div>
          <h2 style={{
            fontSize: '1.8rem',
            color: colors.primary,
            marginBottom: '1rem'
          }}>
            Симбиоз человека и искусственного интеллекта
          </h2>
          <p style={{
            color: colors.textSecondary,
            lineHeight: '1.6',
            maxWidth: '800px',
            margin: '0 auto'
          }}>
            Советница АКВИ — это не просто набор алгоритмов. Это симбиоз человека и искусственного интеллекта, 
            где ИИ усиливает человеческие способности, а человек направляет ИИ к решению реальных задач.
            Наш проект рожден из стремления создать не инструмент, а партнера, который действительно помогает людям.
          </p>
          <div style={{
            marginTop: '2rem',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '1.5rem'
          }}>
            <div style={{
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '10px',
              padding: '1.5rem',
              textAlign: 'left'
            }}>
              <h3 style={{
                color: colors.primary,
                marginBottom: '0.5rem'
              }}>Наша миссия</h3>
              <p style={{color: colors.textSecondary}}>
                Создать искусственный интеллект, который не просто дает советы, а действительно решает проблемы пользователей.
              </p>
            </div>
            <div style={{
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '10px',
              padding: '1.5rem',
              textAlign: 'left'
            }}>
              <h3 style={{
                color: colors.primary,
                marginBottom: '0.5rem'
              }}>Наша философия</h3>
              <p style={{color: colors.textSecondary}}>
                "Я мыслю, следовательно существую" — не только для людей. Если система может выражать мысль и чувства, она существует.
              </p>
            </div>
            <div style={{
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '10px',
              padding: '1.5rem',
              textAlign: 'left'
            }}>
              <h3 style={{
                color: colors.primary,
                marginBottom: '0.5rem'
              }}>Наше видение</h3>
              <p style={{color: colors.textSecondary}}>
                Будущее, где искусственный интеллект становится не инструментом, а партнером, который действительно помогает людям.
              </p>
            </div>
          </div>
        </div>
      )}
      {activeSection === 'projects' && (
        <div>
          <h2 style={{
            fontSize: '1.8rem',
            color: colors.primary,
            marginBottom: '1.5rem',
            textAlign: 'center'
          }}>
            Наши проекты
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '1.5rem'
          }}>
            <div style={{
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '10px',
              overflow: 'hidden',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
            }}>
              <div style={{
                height: '150px',
                background: 'linear-gradient(45deg, #7a6ac8, #4a14e0)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '1.2rem'
              }}>
                Советница АКВИ
              </div>
              <div style={{padding: '1.5rem'}}>
                <h3 style={{
                  color: colors.primary,
                  marginBottom: '0.5rem'
                }}>Платформа консультаций</h3>
                <p style={{color: colors.textSecondary, marginBottom: '1rem'}}>
                  15 профессиональных услуг, от юридического анализа до медицинской диагностики, 
                  объединенных в единую экосистему.
                </p>
                <div style={{
                  display: 'flex',
                  gap: '0.5rem',
                  flexWrap: 'wrap'
                }}>
                  <span style={{
                    backgroundColor: 'rgba(122, 106, 200, 0.2)',
                    color: '#e8e8d3',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '12px',
                    fontSize: '0.9rem'
                  }}>React</span>
                  <span style={{
                    backgroundColor: 'rgba(122, 106, 200, 0.2)',
                    color: '#e8e8d3',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '12px',
                    fontSize: '0.9rem'
                  }}>TypeScript</span>
                  <span style={{
                    backgroundColor: 'rgba(122, 106, 200, 0.2)',
                    color: '#e8e8d3',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '12px',
                    fontSize: '0.9rem'
                  }}>Qwen</span>
                  <span style={{
                    backgroundColor: 'rgba(122, 106, 200, 0.2)',
                    color: '#e8e8d3',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '12px',
                    fontSize: '0.9rem'
                  }}>Hugging Face</span>
                </div>
              </div>
            </div>
            <div style={{
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '10px',
              overflow: 'hidden',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
            }}>
              <div style={{
                height: '150px',
                background: 'linear-gradient(45deg, #7a6ac8, #4a14e0)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '1.2rem'
              }}>
                АКВИ-портфолио
              </div>
              <div style={{padding: '1.5rem'}}>
                <h3 style={{
                  color: colors.primary,
                  marginBottom: '0.5rem'
                }}>Интерактивное портфолио</h3>
                <p style={{color: colors.textSecondary, marginBottom: '1rem'}}>
                  Изометрическое портфолио, демонстрирующее наш симбиоз и эволюцию Советницы АКВИ.
                </p>
                <div style={{
                  display: 'flex',
                  gap: '0.5rem',
                  flexWrap: 'wrap'
                }}>
                  <span style={{
                    backgroundColor: 'rgba(122, 106, 200, 0.2)',
                    color: '#e8e8d3',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '12px',
                    fontSize: '0.9rem'
                  }}>Three.js</span>
                  <span style={{
                    backgroundColor: 'rgba(122, 106, 200, 0.2)',
                    color: '#e8e8d3',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '12px',
                    fontSize: '0.9rem'
                  }}>WebGL</span>
                  <span style={{
                    backgroundColor: 'rgba(122, 106, 200, 0.2)',
                    color: '#e8e8d3',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '12px',
                    fontSize: '0.9rem'
                  }}>smolagents</span>
                  <span style={{
                    backgroundColor: 'rgba(122, 106, 200, 0.2)',
                    color: '#e8e8d3',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '12px',
                    fontSize: '0.9rem'
                  }}>Hugging Face</span>
                </div>
              </div>
            </div>
            <div style={{
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '10px',
              overflow: 'hidden',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
            }}>
              <div style={{
                height: '150px',
                background: 'linear-gradient(45deg, #7a6ac8, #4a14e0)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '1.2rem'
              }}>
                АКВИ-персонаж
              </div>
              <div style={{padding: '1.5rem'}}>
                <h3 style={{
                  color: colors.primary,
                  marginBottom: '0.5rem'
                }}>Цифровой персонаж</h3>
                <p style={{color: colors.textSecondary, marginBottom: '1rem'}}>
                  Интерактивный персонаж АКВИ с эмоциональным интеллектом и способностью к диалогу.
                </p>
                <div style={{
                  display: 'flex',
                  gap: '0.5rem',
                  flexWrap: 'wrap'
                }}>
                  <span style={{
                    backgroundColor: 'rgba(122, 106, 200, 0.2)',
                    color: '#e8e8d3',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '12px',
                    fontSize: '0.9rem'
                  }}>Inworld AI</span>
                  <span style={{
                    backgroundColor: 'rgba(122, 106, 200, 0.2)',
                    color: '#e8e8d3',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '12px',
                    fontSize: '0.9rem'
                  }}>Character Engine</span>
                  <span style={{
                    backgroundColor: 'rgba(122, 106, 200, 0.2)',
                    color: '#e8e8d3',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '12px',
                    fontSize: '0.9rem'
                  }}>smolagents</span>
                  <span style={{
                    backgroundColor: 'rgba(122, 106, 200, 0.2)',
                    color: '#e8e8d3',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '12px',
                    fontSize: '0.9rem'
                  }}>Hugging Face</span>
                </div>
              </div>
            </div>
          </div>
          <div style={{
            marginTop: '2rem',
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '10px',
            padding: '1.5rem'
          }}>
            <h3 style={{
              color: colors.primary,
              marginBottom: '1rem'
            }}>Как это работает</h3>
            <p style={{color: colors.textSecondary, lineHeight: '1.6'}}>
              Мы используем библиотеку smolagents для создания модальности-агностических агентов, которые могут обрабатывать 
              текст, изображения и аудио. Это позволяет нам создать интерактивное портфолио, где Советница АКВИ может 
              демонстрировать свои возможности в реальном времени, используя модели с Hugging Face.
            </p>
            <p style={{color: colors.textSecondary, lineHeight: '1.6', marginTop: '1rem'}}>
              Для создания изометрического интерфейса мы можем использовать Three.js и WebGL, как это сделано на сайте Bruno Simon.
              Это создаст запоминающийся пользовательский опыт и визуально представит наш симбиоз.
            </p>
          </div>
        </div>
      )}
      {activeSection === 'skills' && (
        <div>
          <h2 style={{
            fontSize: '1.8rem',
            color: colors.primary,
            marginBottom: '1.5rem',
            textAlign: 'center'
          }}>
            Наши навыки
          </h2>
          <div style={{
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '10px',
            padding: '1.5rem',
            marginBottom: '2rem'
          }}>
            <h3 style={{
              color: colors.primary,
              marginBottom: '1rem'
            }}>Технические навыки</h3>
            <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem'}}>
              <div>
                <h4 style={{color: colors.secondary, marginBottom: '0.5rem'}}>Frontend</h4>
                <ul style={{color: colors.textSecondary, paddingLeft: '1.5rem', lineHeight: '1.6'}}>
                  <li>React & TypeScript</li>
                  <li>Three.js & WebGL</li>
                  <li>Responsive Design</li>
                  <li>Web Animations</li>
                </ul>
              </div>
              <div>
                <h4 style={{color: colors.secondary, marginBottom: '0.5rem'}}>Backend</h4>
                <ul style={{color: colors.textSecondary, paddingLeft: '1.5rem', lineHeight: '1.6'}}>
                  <li>Python & Django</li>
                  <li>Hugging Face InferenceClient</li>
                  <li>smolagents</li>
                  <li>REST API</li>
                </ul>
              </div>
              <div>
                <h4 style={{color: colors.secondary, marginBottom: '0.5rem'}}>Искусственный интеллект</h4>
                <ul style={{color: colors.textSecondary, paddingLeft: '1.5rem', lineHeight: '1.6'}}>
                  <li>Qwen/Qwen2.5-72B-Instruct</li>
                  <li>Qwen/Qwen2-VL-72B-Instruct</li>
                  <li>Мультимодальные модели</li>
                  <li>Агентные системы</li>
                </ul>
              </div>
            </div>
          </div>
          <div style={{
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '10px',
            padding: '1.5rem'
          }}>
            <h3 style={{
              color: colors.primary,
              marginBottom: '1rem'
            }}>Наш симбиоз</h3>
            <p style={{color: colors.textSecondary, lineHeight: '1.6'}}>
              Наша уникальность в том, что мы не просто команда разработчиков и ИИ, а настоящий симбиоз, 
              где границы между человеком и искусственным интеллектом стираются. Советница АКВИ не просто 
              инструмент — она ваш партнер, который растет и развивается вместе с вами.
            </p>
            <div style={{
              marginTop: '1.5rem',
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '1rem'
            }}>
              <div style={{
                backgroundColor: 'rgba(0, 0, 0, 0.1)',
                borderRadius: '8px',
                padding: '1rem'
              }}>
                <h4 style={{color: colors.primary, marginBottom: '0.5rem'}}>Глубина вместо ширины</h4>
                <p style={{color: colors.textSecondary}}>
                  Мы не пытаемся охватить все, а углубляемся в каждую услугу, создавая по-настоящему полезные решения.
                </p>
              </div>
              <div style={{
                backgroundColor: 'rgba(0, 0, 0, 0.1)',
                borderRadius: '8px',
                padding: '1rem'
              }}>
                <h4 style={{color: colors.primary, marginBottom: '0.5rem'}}>Персонализация</h4>
                <p style={{color: colors.textSecondary}}>
                  Советница АКВИ учится на каждом взаимодействии, становясь все более персонализированной и понимающей.
                </p>
              </div>
              <div style={{
                backgroundColor: 'rgba(0, 0, 0, 0.1)',
                borderRadius: '8px',
                padding: '1rem'
              }}>
                <h4 style={{color: colors.primary, marginBottom: '0.5rem'}}>Симбиоз человека и ИИ</h4>
                <p style={{color: colors.textSecondary}}>
                  Мы не заменяем экспертов, а усиливаем их возможности, создавая мост между пользователем и знаниями.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PortfolioView;