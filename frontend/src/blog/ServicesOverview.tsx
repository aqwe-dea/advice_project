import React from 'react';
import { colors } from "../theme";
import crystal from '../crystal-symbiosis.jpg';
import logo from '../logo.svg';

function ServicesOverview() {
    return (
    <div className="blog">
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
            Советница АКВИ И это статья обзор 15 услуг нашей платформы
          </h1>
          <img src={logo} alt="Логотип Советницы АКВИ" className="about-logo" />
          <p style={{
          fontSize: '1.2rem',
          color: colors.textSecondary,
          maxWidth: '700px',
          margin: '0 auto'
          }}>
          Здесь вы найдете интересные статьи которые возможно вам помогут в жизни или при решении задач.
          </p>
        </div>
        <h2>Наша статья под кристаллом</h2>
    
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
              Статья обзор 15 услуг платформы
            </h2>
            <p style={{color: colors.textSecondary, lineHeight: '1.6'}}>
              [Статья №2]
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
              Ниже ссылки на наши услуги и наших агентов, а также генераторы, возможно вам пригодится.
            </h2>
            <p style={{color: colors.textSecondary, lineHeight: '1.6'}}>
            [ссылка №1]
            [ссылка №2]
            [ссылка №3]
            [ссылка №4]
            [ссылка №5]
            </p>
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
            Интересные статьи?
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
            Попробовать
          </button>
          <p>Далее идет проверка компонентов</p>
        </div>
      </div>
    </div>
    );
}

export default ServicesOverview;