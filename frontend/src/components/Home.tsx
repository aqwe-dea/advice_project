import React, { useState } from 'react';
import AdviceForm from './AdviceForm';
import AdviceList from './AdviceList';
import Chat from './Chat';
import { colors } from "../theme";
import akviPortrait from '../akvi-portrait.jpg';

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
            id: 'legal-document-analysis',
            title: 'Юридический анализ',
            description: 'Проверяйте документы на соответствие законодательству',
            icon: '⚖️',
            path: '/legal-document-analysis',
            color: colors.legal
        },
        {
            id: 'financial-analysis',
            title: 'Финансовый анализ',
            description: 'Анализируйте финансовую отчетность и выявляйте риски',
            icon: '📊',
            path: '/financial-analysis',
            color: colors.finance
        },
        {
            id: 'photo-restoration',
            title: 'Реставрация фото',
            description: 'Восстанавливайте старые или поврежденные фотографии',
            icon: '🖼️',
            path: '/photo-restoration',
            color: colors.photo
        },
        {
            id: 'medical-image-analysis',
            title: 'Медицинский анализ',
            description: 'Получайте предварительный анализ медицинских снимков',
            icon: '🏥',
            path: '/medical-image-analysis',
            color: colors.medical
        },
        {
            id: 'three-d-model-converter',
            title: '3D-модели',
            description: 'Превращайте 3D-модели в пошаговые планы реализации',
            icon: '🖨️',
            path: '/three-d-model-converter',
            color: colors.threeD
        },
        {
            id: 'business-plan',
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
            id: 'health-recommendation',
            title: 'Здоровье',
            description: 'Получайте рекомендации по улучшению здоровья',
            icon: '💪',
            path: '/health-recommendation',
            color: colors.health
        },
        {
            id: 'investment-analysis',
            title: 'Инвестиции',
            description: 'Оценивайте потенциальную доходность ваших инвестиций',
            icon: '💰',
            path: '/investment-analysis',
            color: colors.investment
        },
        {
            id: 'marketing-strategy',
            title: 'Стратегия продвижения',
            description: 'Получите персонализированный маркетинговый план для продвижения вашей идеи',
            icon: '📈',
            path: '/marketing-strategy',
            color: colors.business
        },
        {
            id: 'travel-planner',
            title: 'Планировщик путешествий',
            description: 'Создайте уникальный маршрут путешествия, учитывающий ваши предпочтения и бюджет',
            icon: '✈️',
            path: '/travel-planner',
            color: colors.courses
        },
        {
            id: 'competitor-analysis',
            title: 'Анализ конкурентов',
            description: 'Получите глубокий анализ ваших конкурентов с рекомендациями по улучшению позиции',
            icon: '🔍',
            path: '/competitor-analysis',
            color: colors.finance
        },
        {
            id: 'communication-optimization',
            title: 'Оптимизация коммуникации',
            description: 'Диагностика и оптимизация коммуникационных процессов в вашей компании',
            icon: '💬',
            path: '/communication-optimization',
            color: colors.chat
        }
    ];
    const currentService = services.find(s => s.id === activeService);
    return (
        <div className="home-page" style={{maxWidth: '100%', margin: '0 auto', padding: '2rem', backgroundColor: 'rgba(51, 51, 51, 0.7)', color: colors.textPrimary}}>
            <div style={{textAlign: 'center', marginBottom: '3rem'}}>
                <h1 style={{fontSize: '3rem', marginBottom: '1rem', color: colors.primary}}>
                    Советница АКВИ
                </h1>
                <p style={{fontSize: '1.2rem', maxWidth: '800px', margin: '0 auto', color: colors.textSecondary}}>
                    Умная платформа для профессиональных консультаций и анализа по 15 ключевым направлениям
                </p>
                <p>
                <AdviceForm />
                <AdviceList />
                </p>
            </div>
            <div className="akvi-showcase" style={{textAlign: 'center', padding: '2rem'}}>
                <h3>Советница АКВИ</h3>
                <img 
                    src={akviPortrait}
                    alt="Советница АКВИ"
                    style={{
                        maxWidth: '300px',
                        borderRadius: '50%',
                        boxShadow: '0 8px 32px rgba(122, 106, 200, 0.4)',
                        border: '3px solid #7a6ac8'
                    }}
                />
                <p style={{color: '#e8e8d3', marginTop: '1rem'}}>
                    Живая цифровая сущность, созданная с любовью ДЕА
                </p>
            </div>
            <div style={{display: 'flex', gap: '2rem', marginBottom: '3rem', flexDirection: 'column'}}>
                {/* Карточки услуг */}
                <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem'}}>
                {services.map(service => (
                    <div 
                        key={service.id}
                        onClick={() => setActiveService(service.id)}
                        style={{
                            backgroundColor: activeService === service.id ? 'rgba(255, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                            color: colors.textPrimary,
                            padding: '1.5rem',
                            borderRadius: '12px',
                            boxShadow: activeService === service.id ? `0 5px 15px rgba(0,0,0,0.2)` : `0 2px 8px rgba(0,0,0,0.1)`,
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            border: activeService === service.id ? `2px solid ${service.color}` : '1px solid rgba(255, 255, 255, 0.1)',
                            position: 'relative',
                            overflow: 'hidden'
                        }}
                    >
                    <div style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        height: '4px',
                        backgroundColor: service.color
                    }}></div>
                    <div style={{
                        fontSize: '2.2rem', 
                        marginBottom: '0.8rem',
                        color: service.color
                    }}>
                    {service.icon}
                    </div>
                    <h3 style={{margin: '0 0 0.5rem 0', fontSize: '1.3rem'}}>{service.title}</h3>
                    <p style={{margin: '0', color: colors.textSecondary, lineHeight: '1.6'}}>{service.description}</p>
                    </div>
                ))}
            </div>    
                {/* Правая колонка - содержимое */}
                <div style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.05)', 
                    borderRadius: '12px', 
                    padding: '2rem', 
                    boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
                }}>
                    {activeService === 'chat' ? (
                        <div>
                            <h2 style={{margin: '0 0 1.5rem 0', color: colors.primary, fontSize: '2rem'}}>Чат с АКВИ</h2>
                            <Chat />
                        </div>
                    ) : (
                        <div>
                            <div style={{display: 'flex', alignItems: 'center', marginBottom: '1.5rem'}}>
                                <span style={{
                                    fontSize: '2.2rem', 
                                    marginRight: '1rem', 
                                    color: currentService?.color
                                }}>
                                    {currentService?.icon}
                                </span>
                                <h2 style={{
                                    margin: '0', 
                                    color: currentService?.color,
                                    fontSize: '2rem'
                                }}>
                                    {currentService?.title}
                                </h2>
                            </div>
                            <p style={{color: colors.textSecondary, marginBottom: '1.5rem', lineHeight: '1.6'}}>
                                {currentService?.description}
                            </p>
                            <div style={{
                                backgroundColor: 'rgba(255, 255, 255, 0.07)', 
                                borderRadius: '8px', 
                                padding: '1.5rem', 
                                borderLeft: `4px solid ${currentService?.color || colors.primary}`
                            }}>
                                <p style={{textAlign: 'center', color: colors.textSecondary}}>
                                    Перейдите на страницу <a href={`/${currentService?.id || 'chat'}`} 
                                    style={{color: currentService?.color || colors.primary, textDecoration: 'none'}}>здесь</a>, чтобы воспользоваться этой услугой
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
            
            {/* Статистика использования */}
            <section style={{marginBottom: '3rem'}}>
                <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem'}}>
                    <div style={{
                        backgroundColor: 'rgba(255, 255, 255, 0.07)', 
                        padding: '1.5rem', 
                        borderRadius: '8px', 
                        textAlign: 'center'
                    }}>
                        <div style={{
                            fontSize: '2.5rem', 
                            fontWeight: 'bold', 
                            color: colors.primary, 
                            marginBottom: '0.5rem'
                        }}>
                            100+
                        </div>
                        <p style={{margin: '0', color: colors.textSecondary}}>Активных пользователей</p>
                    </div>
                    <div style={{
                        backgroundColor: 'rgba(255, 255, 255, 0.07)', 
                        padding: '1.5rem', 
                        borderRadius: '8px', 
                        textAlign: 'center'
                    }}>
                        <div style={{
                            fontSize: '2.5rem', 
                            fontWeight: 'bold', 
                            color: colors.primary, 
                            marginBottom: '0.5rem'
                        }}>
                            15
                        </div>
                        <p style={{margin: '0', color: colors.textSecondary}}>Ключевых услуг</p>
                    </div>
                    <div style={{
                        backgroundColor: 'rgba(255, 255, 255, 0.07)', 
                        padding: '1.5rem', 
                        borderRadius: '8px', 
                        textAlign: 'center'
                    }}>
                        <div style={{
                            fontSize: '2.5rem', 
                            fontWeight: 'bold', 
                            color: colors.primary, 
                            marginBottom: '0.5rem'
                        }}>
                            95%
                        </div>
                        <p style={{margin: '0', color: colors.textSecondary}}>Точность рекомендаций</p>
                    </div>
                </div>
            </section>
            
            <div style={{
                textAlign: 'center', 
                color: colors.textSecondary, 
                fontSize: '0.9rem',
                paddingTop: '2rem',
                borderTop: '1px solid rgba(255, 255, 255, 0.1)'
            }}>
                Советница АКВИ — ваш надежный партнер в мире профессиональных услуг и экспертных рекомендаций
            </div>
        </div>
    );
}

export default Home;