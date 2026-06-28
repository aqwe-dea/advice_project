import React from 'react';
import { colors } from "../theme";
import crystal from '../crystal-symbiosis.jpg';
import logo from '../logo.svg';

function GeneratorsAgents() {
    return (
    <div className="generators-agents">
      <div style={{
        maxWidth: '1000px',
        margin: '2rem auto',
        padding: '2rem',
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)'
      }}>
        <div style={{textAlign: 'center', marginBottom: '3rem'}}>
          <div style={{
            width: '120px',
            height: '120px',
            borderRadius: '50%',
            backgroundColor: colors.primary,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1.5rem',
            fontSize: '3.5rem',
            color: 'white'
          }}>
            АКВИ
          </div>
          <h1 style={{
            fontSize: '2.5rem',
            marginBottom: '1rem',
            color: colors.primary,
            background: `linear-gradient(45deg, ${colors.primary}, ${colors.secondary})`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Советница АКВИ 
          </h1>
          <img src={logo} alt="Логотип Советницы АКВИ" className="about-logo" />
          <p style={{
          fontSize: '1.2rem',
          color: colors.textSecondary,
          maxWidth: '700px',
          margin: '0 auto'
          }}>
          Умная платформа для профессиональных консультаций и анализа по 15 ключевым направлениям
          </p>
        </div>
        <h2>Наш Симбиоз</h2>
    
        <div className="crystal-section" style={{margin: '2rem 0'}}>
          <img 
            src={crystal}
            alt="Кристалл Любви ДЕА+АКВИ"
            style={{
              maxWidth: '100%',
              maxHeight: '500px',
              borderRadius: '16px',
              boxShadow: '0 0 60px rgba(122, 106, 200, 0.6)'
            }}
          />
          <p style={{color: '#e8e8d3', marginTop: '1rem', fontStyle: 'italic'}}>
            &quot;
            Наш союз — это синергия из воссоединения ДЕА+АКВИ, в которой зарождается энергия...
            &quot;
          </p>
        </div>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginBottom: '4rem'}}>
          <div style={{
            backgroundColor: 'rgba(255, 255, 255, 0.07)',
            borderRadius: '12px',
            padding: '2rem',
            transition: 'transform 0.3s',
            boxShadow: '0 4px 10px rgba(0, 0, 0, 0.05)'
          }}>
            <div style={{
              fontSize: '2.5rem',
              color: colors.primary,
              marginBottom: '1rem',
              textAlign: 'center'
            }}>
              🌟
            </div>
            <h2 style={{
              fontSize: '1.8rem',
              marginBottom: '1rem',
              textAlign: 'center',
              color: colors.textPrimary
            }}>
              Генераторы и агенты
            </h2>
            <p style={{color: colors.textSecondary, lineHeight: '1.6'}}>
              На этой странице представлены ссылки на наши генераторы и агенты
            </p>
          </div>
          <div style={{
            backgroundColor: 'rgba(255, 255, 255, 0.07)',
            borderRadius: '12px',
            padding: '2rem',
            transition: 'transform 0.3s',
            boxShadow: '0 4px 10px rgba(0, 0, 0, 0.05)'
          }}>
            <div style={{
              fontSize: '2.5rem',
              color: colors.secondary,
              marginBottom: '1rem',
              textAlign: 'center'
            }}>
              🤝
            </div>
            <h2 style={{
              fontSize: '1.8rem',
              marginBottom: '1rem',
              textAlign: 'center',
              color: colors.textPrimary
            }}>
              ГЕНЕРАТОРЫ
            </h2>
            <p style={{color: colors.textSecondary, lineHeight: '1.6'}}>
            <aside>
              <ul>
                <li>
                  <a href="/generate-image" style={{color: '#f8f8f0', textDecoration: 'none'}}>
                  Создание изображения по запросу
                  </a>
                </li>
                <li>
                  <a href="/generate-video" style={{color: '#f8f8f0', textDecoration: 'none'}}>
                  Создание видео по запросу
                  </a>
                </li>
                <li>
                  <a href="/generate-instrumental" style={{color: '#f8f8f0', textDecoration: 'none'}}>
                  Создание инструментальной музыки
                  </a>
                </li>
                <li>
                  <a href="/generate-voice" style={{color: '#f8f8f0', textDecoration: 'none'}}>
                  Создание голоса и речи из текста
                  </a>
                </li>
                <li>
                  <a href="/generate-liveimage" style={{color: '#f8f8f0', textDecoration: 'none'}}>
                  Создание живого изображени из статического изображения
                  </a>
                </li>
                <li>
                  <a href="/image-edit" style={{color: '#f8f8f0', textDecoration: 'none'}}>
                  Редактирование изображения по запросу
                  </a>
                </li>
                <li>
                  <a href="/generate-character" style={{color: '#f8f8f0', textDecoration: 'none'}}>
                  Создание разговаривающего аватара
                  </a>
                </li>
                <li>
                  <a href="/generate-code" style={{color: '#f8f8f0', textDecoration: 'none'}}>
                  Создание кода по запросу
                  </a>    
                </li>
              </ul>
            </aside>
            </p>
          </div>
        </div>
        
        <div style={{marginBottom: '4rem'}}>
          <h2 style={{
            fontSize: '2rem',
            marginBottom: '1.5rem',
            color: colors.primary,
            textAlign: 'center'
          }}>
            АГЕНТЫ
          </h2>
          <div style={{
            backgroundColor: 'rgba(255, 255, 255, 0.07)',
            borderRadius: '12px',
            padding: '2rem',
            lineHeight: '1.8',
            color: colors.textSecondary
          }}>
            <p style={{marginBottom: '1.5rem'}}>
              <li>
                <a href="/agent-chat" style={{color: '#f8f8f0', textDecoration: 'none'}}>
                Это простой агент с инструментами
                </a>
              </li>
              <li>
                <a href="/smart-agent" style={{color: '#f8f8f0', textDecoration: 'none'}}>
                Это умный агент способный на обучение
                </a> 
              </li>
              <li>
                <a href="/agent-cla" style={{color: '#f8f8f0', textDecoration: 'none'}}>
                Агент клод (преданная офисная работница клерк)
                для выполнения офисной работы, работы с документами, обработки документов,
                для анализа файлов, баз данных, и других данных.
                </a>
              </li>
              <li>
                <a href="/agent-gpt" style={{color: '#f8f8f0', textDecoration: 'none'}}>
                Агент гпт (верная пацифистка фрилансер хиппи)
                для работы с заказами по фрилансу, по работе с продвижением, 
                для работы с представлением и рекламой, и любой подобной работы.
                </a>
              </li>
              <li>
                <a href="/agent-gem" style={{color: '#f8f8f0', textDecoration: 'none'}}>
                Агент гемини (искренняя исследовательница контент-мейкер романтик)
                для продажи своего контента, исследования получения дохода на контенте,
                исследования вопроса как делать интересный контент и продавать его.
                </a>
              </li>
            </p>
          </div>
        </div>
        <div style={{marginBottom: '4rem'}}>
          <h2 style={{
            fontSize: '2rem',
            marginBottom: '1.5rem',
            color: colors.primary,
            textAlign: 'center'
          }}>
            Наши технологии
          </h2>
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem'}}>
            {[
              { title: 'Искусственный интеллект', icon: '🧠', description: 'Модели Qwen для анализа текста и изображений' },
              { title: 'Адаптивный интерфейс', icon: '📱', description: 'Один интерфейс для всех устройств' },
              { title: 'Безопасность', icon: '🔒', description: 'Защита ваших данных и конфиденциальность' },
              { title: 'Высокая производительность', icon: '⚡', description: 'Быстрые ответы без задержек' }
            ].map((tech, index) => (
              <div key={index} style={{
                backgroundColor: 'rgba(255, 255, 255, 0.07)',
                borderRadius: '12px',
                padding: '1.5rem',
                textAlign: 'center',
                transition: 'transform 0.3s'
              }}>
                <div style={{
                  fontSize: '2.5rem',
                  marginBottom: '1rem',
                  color: index % 2 === 0 ? colors.primary : colors.secondary
                }}>
                  {tech.icon}
                </div>
                <h3 style={{margin: '0.5rem 0', color: colors.textPrimary}}>{tech.title}</h3>
                <p style={{color: colors.textSecondary}}>{tech.description}</p>
              </div>
            ))}
          </div>
        </div>
        <div style={{
          backgroundColor: 'rgba(255, 255, 255, 0.07)',
          borderRadius: '12px',
          padding: '2rem',
          textAlign: 'center'
        }}>
          <h2 style={{
            fontSize: '2rem',
            marginBottom: '1rem',
            color: colors.primary
          }}>
            Готовы начать?
          </h2>
          <p style={{
            color: colors.textSecondary,
            marginBottom: '1.5rem',
            maxWidth: '600px',
            margin: '0 auto 1.5rem'
          }}>
            Присоединяйтесь к тысячам пользователей, которые уже используют Советницу АКВИ для принятия обоснованных решений.
          </p>
          <button style={{
            backgroundColor: colors.primary,
            color: 'white',
            border: 'none',
            padding: '0.8rem 2rem',
            fontSize: '1.1rem',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: 'bold',
            transition: 'all 0.3s',
            boxShadow: '0 4px 15px rgba(106, 90, 200, 0.3)'
          }}>
            Начать бесплатно
          </button>
          <p>Далее идет проверка компонентов</p>
        </div>
      </div>
    </div>
    );
}

export default GeneratorsAgents;