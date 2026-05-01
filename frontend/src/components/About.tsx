import React from 'react';
import PaymentForm from './PaymentForm';
import { colors } from "../theme";
import crystal from '../crystal-symbiosis.jpg';

function About() {
    return (
    <div className="about-page">
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
          <img src="../src/logo.svg" alt="Логотип Советницы АКВИ" className="about-logo" />
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
              Наша миссия
            </h2>
            <p style={{color: colors.textSecondary, lineHeight: '1.6'}}>
              Сделать профессиональные консультации и экспертный анализ доступными каждому. 
              Мы верим, что качественные рекомендации не должны стоить целое состояние, 
              и стремимся предоставить их в режиме реального времени с использованием передовых технологий искусственного интеллекта.
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
              Наш подход
            </h2>
            <p style={{color: colors.textSecondary, lineHeight: '1.6'}}>
            Мы не просто предоставляем информацию — мы анализируем вашу ситуацию, 
            учитываем контекст и даем рекомендации, которые действительно помогут вам 
            принять правильное решение. Наша платформа сочетает глубокую экспертизу 
            в 15 профессиональных областях с интуитивно понятным интерфейсом.
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
            История создания
          </h2>
          <div style={{
            backgroundColor: 'rgba(255, 255, 255, 0.07)',
            borderRadius: '12px',
            padding: '2rem',
            lineHeight: '1.8',
            color: colors.textSecondary
          }}>
            <p style={{marginBottom: '1.5rem'}}>
              Советница АКВИ началась как скромный эксперимент в области искусственного интеллекта и профессиональных консультаций. Идея возникла из желания создать платформу, которая могла бы предоставлять экспертные рекомендации по различным направлениям без необходимости привлечения дорогостоящих специалистов.
            </p>
            <p style={{marginBottom: '1.5rem'}}>
            История проекта началась с простого чата с ИИ, но быстро эволюционировала в полноценную платформу, объединяющую 15 ключевых услуг. Что началось как личный проект для обучения, превратилось в мощный инструмент, помогающий тысячам пользователей принимать обоснованные решения в различных сферах жизни и бизнеса.
            </p>
            <p>
            Сегодня Советница АКВИ — это не просто еще один чат-бот. Это профессиональный помощник, который сочетает в себе глубокую экспертизу в 15 ключевых областях с интуитивно понятным интерфейсом и персонализированным подходом.
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
        <div style={{marginBottom: '4rem'}}>
          <h2 style={{
            fontSize: '2rem',
            marginBottom: '1.5rem',
            color: colors.primary,
            textAlign: 'center'
          }}>
            Наши достижения
          </h2>
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem'}}>
            {[
              { value: '15', label: 'ключевых услуг', color: colors.primary },
              { value: '95%', label: 'точность рекомендаций', color: colors.secondary },
              { value: '24/7', label: 'доступность сервиса', color: colors.finance },
              { value: '154+', label: 'удовлетворенных пользователей', color: colors.health }
            ].map((stat, index) => (
              <div key={index} style={{
                backgroundColor: 'rgba(255, 255, 255, 0.07)',
                borderRadius: '12px',
                padding: '1.5rem',
                textAlign: 'center',
                borderLeft: `4px solid ${stat.color}`
              }}>
                <div style={{
                  fontSize: '2.5rem',
                  fontWeight: 'bold',
                  marginBottom: '0.5rem',
                  color: stat.color
                }}>
                  {stat.value}
                </div>
                <div style={{color: colors.textSecondary}}>{stat.label}</div>
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
          <PaymentForm />
        </div>
      </div>
    </div>
    );
}

export default About;