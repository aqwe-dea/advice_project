import React, { useState } from 'react';
import AdviceForm from './AdviceForm';
import AdviceList from './AdviceList';
import Chat from './Chat';
import { colors } from "../theme";

function Home({ onSuccess }: { onSuccess?: () => void }) {
    const [activeService, setActiveService] = useState<string>('chat');
    const services = [
        {
            id: 'chat',
            title: 'Чат с АКВИ',
            description: 'Получайте мгновенные ответы на ваши вопросы от ИИ',
            icon: '💬',
            path: '/chat',
            color: colors.chat
        },
        {
            id: 'course',
            title: 'Генерация курсов',
            description: 'Получайте персональные учебные курсы по любой теме',
            icon: '📚',
            path: '/course',
            color: colors.courses
        },
        {
            id: 'legal',
            title: 'Юридический анализ',
            description: 'Проверяйте документы на соответствие законодательству',
            icon: '⚖️',
            path: '/legal-document-analysis',
            color: colors.legal
        },
        {
            id: 'finance',
            title: 'Финансовый анализ',
            description: 'Анализируйте финансовую отчетность и выявляйте риски',
            icon: '📊',
            path: '/financial-analysis',
            color: colors.finance
        },
        {
            id: 'photo',
            title: 'Реставрация фото',
            description: 'Восстанавливайте старые или поврежденные фотографии',
            icon: '🖼️',
            path: '/photo-restoration',
            color: colors.photo
        },
        {
            id: 'medical',
            title: 'Медицинский анализ',
            description: 'Получайте предварительный анализ медицинских снимков',
            icon: '🏥',
            path: '/medical-image-analysis',
            color: colors.medical
        },
        {
            id: '3d',
            title: '3D-модели',
            description: 'Превращайте 3D-модели в пошаговые планы реализации',
            icon: '🖨️',
            path: '/three-d-model-converter',
            color: colors.threeD
        },
        {
            id: 'business',
            title: 'Бизнес-планы',
            description: 'Создавайте профессиональные бизнес-планы с SWOT-анализом',
            icon: '📈',
            path: '/business-plan',
            color: colors.business
        },
        {
            id: 'presentation',
            title: 'Презентации',
            description: 'Получайте готовую структуру профессиональных презентаций',
            icon: '📊',
            path: '/presentation',
            color: colors.presentation
        },
        {
            id: 'health',
            title: 'Здоровье',
            description: 'Получайте рекомендации по улучшению здоровья',
            icon: '💪',
            path: '/health-recommendation',
            color: colors.health
        },
        {
            id: 'investment',
            title: 'Инвестиции',
            description: 'Оценивайте потенциальную доходность ваших инвестиций',
            icon: '💰',
            path: '/investment-analysis',
            color: colors.investment
        }
    ];
    return (
        <div className="home-page" style={{maxWidth: '100%', margin: '0 auto', padding: '2rem', 
            background: `linear-gradient(135deg, ${colors.background} 0%, ${colors.backgroundLight} 100%)`, 
            color: colors.textPrimary}}>
            <div style={{textAlign: 'center', marginBottom: '3rem'}}>
                <h1 style={{fontSize: '3rem', marginBottom: '1rem', color: colors.primary}}>
                    Советница АКВИ
                </h1>
                <p style={{fontSize: '1.2rem', maxWidth: '800px', margin: '0 auto'}}>
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
                            backgroundColor: activeService === service.id ? service.color : 'rgba(255, 255, 255, 0.07)',
                            color: activeService === service.id ? '#000000' : colors.textPrimary,
                            padding: '1.2rem',
                            borderRadius: '8px',
                            boxShadow: `0 2px 8px rgba(0,0,0,0.3)`,
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            border: activeService === service.id ? `2px solid ${service.color}` : '1px solid rgba(255, 255, 255, 0.15)',
                            marginBottom: '1rem'
                        }}
                        >
                        <div style={{fontSize: '2rem', marginBottom: '0.5rem'}}>{service.icon}</div>
                        <h3 style={{margin: '0 0 0.5rem 0'}}>{service.title}</h3>
                        <p style={{margin: '0'}}>{service.description}</p>
                        </div>
                    ))}
                </div>
                <div style={{flex: '1', backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: '10px', padding: '2rem', boxShadow: '0 2px 10px rgba(0,0,0,0.1)'}}>
                    {activeService === 'chat' ? (
                        <div>
                            <h2 style={{margin: '0 0 1.5rem 0', color: colors.primary}}>Чат с АКВИ</h2>
                            <Chat />
                        </div>
                    ) : (
                        <div>
                            <div style={{display: 'flex', alignItems: 'center', marginBottom: '1.5rem'}}>
                                <span style={{fontSize: '2rem', marginRight: '1rem', color: services.find(s => s.id === activeService)?.color}}>
                                    {services.find(s => s.id === activeService)?.icon}
                                </span>
                                <h2 style={{margin: '0', color: services.find(s => s.id === activeService)?.color}}>
                                    {services.find(s => s.id === activeService)?.title}
                                </h2>
                            </div>
                            <p style={{marginBottom: '1.5rem'}}>
                                {services.find(s => s.id === activeService)?.description}
                            </p>
                            <div style={{backgroundColor: 'rgba(255, 255, 255, 0.1)', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)'}}>
                                <p style={{textAlign: 'center'}}>
                                    Перейдите на страницу <a href={services.find(s => s.id === activeService)?.path} 
                                    style={{color: services.find(s => s.id === activeService)?.color, textDecoration: 'none'}}>здесь</a>, чтобы воспользоваться этой услугой
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
            <section style={{marginBottom: '3rem'}}>
                <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem'}}>
                    <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.5rem', borderRadius: '8px', textAlign: 'center'}}>
                        <div style={{fontSize: '2.5rem', fontWeight: 'bold', color: colors.primary, marginBottom: '0.5rem'}}>154</div>
                        <p style={{margin: '0'}}>Активных пользователей</p>
                    </div>
                    <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.5rem', borderRadius: '8px', textAlign: 'center'}}>
                        <div style={{fontSize: '2.5rem', fontWeight: 'bold', color: colors.primary, marginBottom: '0.5rem'}}>11</div>
                        <p style={{margin: '0'}}>Ключевых услуг</p>
                    </div>
                    <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.5rem', borderRadius: '8px', textAlign: 'center'}}>
                        <div style={{fontSize: '2.5rem', fontWeight: 'bold', color: colors.primary, marginBottom: '0.5rem'}}>1245</div>
                        <p style={{margin: '0'}}>Всего запросов</p>
                    </div>
                    <div style={{backgroundColor: 'rgba(255, 255, 255, 0.05)', padding: '1.5rem', borderRadius: '8px', textAlign: 'center'}}>
                        <div style={{fontSize: '2.5rem', fontWeight: 'bold', color: colors.primary, marginBottom: '0.5rem'}}>95%</div>
                        <p style={{margin: '0'}}>Точность рекомендаций</p>
                    </div>
                </div>
            </section>
            <div style={{textAlign: 'center', color: '#7f8c8d', fontSize: '0.9rem'}}>
                Советница АКВИ — ваш надежный партнер в мире профессиональных услуг и экспертных рекомендаций
            </div>
        </div>
    );
}

export default Home;