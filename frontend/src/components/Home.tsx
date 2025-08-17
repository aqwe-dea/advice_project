import React, { useState } from 'react';
import AdviceForm from './AdviceForm';
import AdviceList from './AdviceList';
import Chat from './Chat';

function Home({ onSuccess }: { onSuccess?: () => void }) {
    const [activeService, setActiveService] = useState<string>('chat');
    const services = [
        {
            id: 'chat',
            title: 'Чат с АКВИ',
            description: 'Получайте мгновенные ответы на ваши вопросы от ИИ',
            icon: '💬',
            path: '/chat'
        },
        {
            id: 'course',
            title: 'Генерация курсов',
            description: 'Получайте персональные учебные курсы по любой теме',
            icon: '📚',
            path: '/course'
        },
        {
            id: 'legal',
            title: 'Юридический анализ',
            description: 'Проверяйте документы на соответствие законодательству',
            icon: '⚖️',
            path: '/legal-document-analysis'
        },
        {
            id: 'finance',
            title: 'Финансовый анализ',
            description: 'Анализируйте финансовую отчетность и выявляйте риски',
            icon: '📊',
            path: '/financial-analysis'
        },
        {
            id: 'photo',
            title: 'Реставрация фото',
            description: 'Восстанавливайте старые или поврежденные фотографии',
            icon: '🖼️',
            path: '/photo-restoration'
        },
        {
            id: 'medical',
            title: 'Медицинский анализ',
            description: 'Получайте предварительный анализ медицинских снимков',
            icon: '🏥',
            path: '/medical-image-analysis'
        },
        {
            id: '3d',
            title: '3D-модели',
            description: 'Превращайте 3D-модели в пошаговые планы реализации',
            icon: '🖨️',
            path: '/three-d-model-converter'
        },
        {
            id: 'business',
            title: 'Бизнес-планы',
            description: 'Создавайте профессиональные бизнес-планы с SWOT-анализом',
            icon: '📈',
            path: '/business-plan'
        },
        {
            id: 'presentation',
            title: 'Презентации',
            description: 'Получайте готовую структуру профессиональных презентаций',
            icon: '📊',
            path: '/presentation'
        },
        {
            id: 'health',
            title: 'Здоровье',
            description: 'Получайте рекомендации по улучшению здоровья',
            icon: '💪',
            path: '/health-recommendation'
        },
        {
            id: 'investment',
            title: 'Инвестиции',
            description: 'Оценивайте потенциальную доходность ваших инвестиций',
            icon: '💰',
            path: '/investment-analysis'
        }
    ];
    return (
        <div className="home-page" style={{maxWidth: '1400px', margin: '0 auto', padding: '2rem'}}>
            <div style={{textAlign: 'center', marginBottom: '3rem'}}>
                <h1 style={{fontSize: '3rem', marginBottom: '1rem', color: '#2c3e50'}}>
                    Советница АКВИ
                </h1>
                <p style={{fontSize: '1.2rem', maxWidth: '800px', margin: '0 auto', color: '#7f8c8d'}}>
                    Умная платформа для профессиональных консультаций и анализа по 11 ключевым направлениям
                </p>
                <p>
                <AdviceForm />
                <AdviceList />
                </p>
            </div>
            <div style={{display: 'flex', gap: '2rem', marginBottom: '3rem'}}>
                <div style={{flex: '0 0 300px', display: 'flex', flexDirection: 'column', gap: '1rem'}}>
                    {services.map(service => (
                        <div 
                            key={service.id}
                            onClick={() => setActiveService(service.id)}
                            style={{
                                backgroundColor: activeService === service.id ? '#3498db' : '#f8f9fa',
                                color: activeService === service.id ? 'white' : '#2c3e50',
                                padding: '1.2rem',
                                borderRadius: '8px',
                                boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
                                cursor: 'pointer',
                                transition: 'all 0.3s',
                                border: activeService === service.id ? '2px solid #2980b9' : '1px solid #e0e0e0'
                            }}
                        >
                            <div style={{fontSize: '2rem', marginBottom: '0.5rem'}}>{service.icon}</div>
                            <h3 style={{margin: '0 0 0.5rem 0'}}>{service.title}</h3>
                            <p style={{margin: '0', opacity: activeService === service.id ? '0.9' : '0.7'}}>{service.description}</p>
                        </div>
                    ))}
                </div>
                <div style={{flex: '1', backgroundColor: '#f8f9fa', borderRadius: '10px', padding: '2rem', boxShadow: '0 2px 10px rgba(0,0,0,0.05)'}}>
                    {activeService === 'chat' ? (
                        <div>
                            <h2 style={{margin: '0 0 1.5rem 0', color: '#2c3e50'}}>Чат с АКВИ</h2>
                            <Chat />
                        </div>
                    ) : (
                        <div>
                            <div style={{display: 'flex', alignItems: 'center', marginBottom: '1.5rem'}}>
                                <span style={{fontSize: '2rem', marginRight: '1rem'}}>
                                    {services.find(s => s.id === activeService)?.icon}
                                </span>
                                <h2 style={{margin: '0', color: '#2c3e50'}}>
                                    {services.find(s => s.id === activeService)?.title}
                                </h2>
                            </div>
                            <p style={{color: '#7f8c8d', marginBottom: '1.5rem'}}>
                                {services.find(s => s.id === activeService)?.description}
                            </p>
                            <div style={{backgroundColor: 'white', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)'}}>
                                <p style={{textAlign: 'center', color: '#7f8c8d'}}>
                                    Перейдите на страницу <a href={services.find(s => s.id === activeService)?.path} 
                                    style={{color: '#3498db', textDecoration: 'none'}}>здесь</a>, чтобы воспользоваться этой услугой
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
            <div style={{textAlign: 'center', color: '#7f8c8d', fontSize: '0.9rem'}}>
                Советница АКВИ — ваш надежный партнер в мире профессиональных услуг и экспертных рекомендаций
            </div>
        </div>
    );
}

export default Home;