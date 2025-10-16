import React, { useState, useEffect } from 'react';

const BusinessPlanForm = () => {
  const [formData, setFormData] = useState({
    idea: '',
    type: 'стартап',
    country: 'Россия',
    target_market: 'локальный рынок',
    investment_amount: 'средние инвестиции',
    timeframe: '3 года'
  });
  const [industryData, setIndustryData] = useState({
    industry: '',
    niche: '',
    business_model: 'B2C',
    country: 'Россия'
  });
  const [pitchData, setPitchData] = useState({
    target_investors: 'венчурные инвесторы',
    presentation_time: '5-7 минут',
    country: 'Россия',
    business_plan: 'string'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [industryTemplate, setIndustryTemplate] = useState<any>(null);
  const [pitchDeck, setPitchDeck] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'plan' | 'template' | 'pitch'>('plan');
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    if (activeTab === 'plan') {
      setFormData(prev => ({ ...prev, [name]: value }));
    } else if (activeTab === 'template') {
      setIndustryData(prev => ({ ...prev, [name]: value }));
    } else {
      setPitchData(prev => ({ ...prev, [name]: value }));
    }
  };  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();    
    setIsLoading(true);
    setError(null);    
    try {
      if (activeTab === 'plan') {
        if (!formData.idea.trim()) {
          setError('Пожалуйста, укажите идею бизнеса');
          return;
        }        
        const response = await fetch('/business-plan/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(formData)
        });        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Ошибка при генерации бизнес-плана');
        }        
        const data = await response.json();
        setResult(data);
        setPitchData(prev => ({ ...prev, business_plan: data.business_plan }));
      } 
      else if (activeTab === 'template') {
        if (!industryData.industry.trim()) {
          setError('Пожалуйста, укажите отрасль');
          return;
        }        
        const response = await fetch('/business-plan/industry-templates/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(industryData)
        });        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Ошибка при генерации отраслевого шаблона');
        }        
        const data = await response.json();
        setIndustryTemplate(data);
      }
      else if (activeTab === 'pitch') {
        if (!pitchData.business_plan) {
          setError('Пожалуйста, сначала сгенерируйте бизнес-план');
          return;
        }        
        const response = await fetch('/business-plan/pitch-deck/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(pitchData)
        });        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Ошибка при генерации pitch-дека');
        }        
        const data = await response.json();
        setPitchDeck(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка');
    } finally {
      setIsLoading(false);
    }
  };  
  const renderBusinessPlan = () => {
    if (!result || !result.business_plan) return null;    
    const sections = {
      executive_summary: extractSection(result.business_plan, "## 1. ИСПОЛНИТЕЛЬНОЕ РЕЗЮМЕ", "## 2."),
      business_description: extractSection(result.business_plan, "## 2. ОПИСАНИЕ БИЗНЕСА", "## 3."),
      market_analysis: extractSection(result.business_plan, "## 3. АНАЛИЗ РЫНКА", "## 4."),
      swot: extractSection(result.business_plan, "## 4. SWOT-АНАЛИЗ", "## 5."),
      competitor_analysis: extractSection(result.business_plan, "## 5. КОНКУРЕНТНЫЙ АНАЛИЗ", "## 6."),
      marketing_strategy: extractSection(result.business_plan, "## 6. МАРКЕТИНГОВАЯ СТРАТЕГИЯ", "## 7."),
      operations_plan: extractSection(result.business_plan, "## 7. ПЛАН ОПЕРАЦИЙ", "## 8."),
      organizational_structure: extractSection(result.business_plan, "## 8. ОРГАНИЗАЦИОННАЯ СТРУКТУРА", "## 9."),
      financial_plan: extractSection(result.business_plan, "## 9. ФИНАНСОВЫЙ ПЛАН", "## 10."),
      risks: extractSection(result.business_plan, "## 10. РИСКИ И ИХ МИНИМИЗАЦИЯ", null)
    };    
    return (
      <div className="business-plan">
        <h3>Бизнес-план: {formData.idea}</h3>        
        <div className="section">
          <h4>1. Исполнительное резюме</h4>
          <div className="section-content">{sections.executive_summary || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>2. Описание бизнеса</h4>
          <div className="section-content">{sections.business_description || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>3. Анализ рынка</h4>
          <div className="section-content">{sections.market_analysis || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>4. SWOT-анализ</h4>
          <div className="section-content">{sections.swot || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>5. Конкурентный анализ</h4>
          <div className="section-content">{sections.competitor_analysis || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>6. Маркетинговая стратегия</h4>
          <div className="section-content">{sections.marketing_strategy || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>7. План операций</h4>
          <div className="section-content">{sections.operations_plan || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>8. Организационная структура</h4>
          <div className="section-content">{sections.organizational_structure || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>9. Финансовый план</h4>
          <div className="section-content">{sections.financial_plan || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>10. Риски и их минимизация</h4>
          <div className="section-content">{sections.risks || "Не найдено"}</div>
        </div>        
        <div className="button-group">
          <button 
            onClick={() => {
              setActiveTab('template');
              setIndustryData({
                industry: '',
                niche: '',
                business_model: 'B2C',
                country: formData.country
              });
            }}
            className="generate-button"
          >
            Сгенерировать отраслевой шаблон
          </button>          
          <button 
            onClick={() => {
              setActiveTab('pitch');
              setPitchData({
                business_plan: result.business_plan,
                target_investors: 'венчурные инвесторы',
                presentation_time: '5-7 минут',
                country: formData.country
              });
            }}
            className="generate-button"
          >
            Сгенерировать pitch-дек
          </button>
        </div>
      </div>
    );
  };
  const renderIndustryTemplate = () => {
    if (!industryTemplate || !industryTemplate.industry_template) return null;    
    const sections = {
      industry_features: extractSection(industryTemplate.industry_template, "## 1. ОСОБЕННОСТИ ОТРАСЛИ", "## 2."),
      niche_specifics: extractSection(industryTemplate.industry_template, "## 2. СПЕЦИФИКА НИШИ", "## 3."),
      marketing_plan: extractSection(industryTemplate.industry_template, "## 3. АДАПТИРОВАННЫЙ МАРКЕТИНГОВЫЙ ПЛАН", "## 4."),
      operational_features: extractSection(industryTemplate.industry_template, "## 4. ОПЕРАЦИОННЫЕ ОСОБЕННОСТИ", "## 5."),
      financial_norms: extractSection(industryTemplate.industry_template, "## 5. ФИНАНСОВЫЕ НОРМАТИВЫ", "## 6."),
      startup_recommendations: extractSection(industryTemplate.industry_template, "## 6. РЕКОМЕНДАЦИИ ПО СТАРТУ", null)
    };    
    return (
      <div className="industry-template">
        <h3>Отраслевой шаблон: {industryTemplate.industry} в нише {industryTemplate.niche}</h3>        
        <div className="section">
          <h4>1. Особенности отрасли</h4>
          <div className="section-content">{sections.industry_features || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>2. Специфика ниши</h4>
          <div className="section-content">{sections.niche_specifics || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>3. Адаптированный маркетинговый план</h4>
          <div className="section-content">{sections.marketing_plan || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>4. Операционные особенности</h4>
          <div className="section-content">{sections.operational_features || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>5. Финансовые нормативы</h4>
          <div className="section-content">{sections.financial_norms || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>6. Рекомендации по старту</h4>
          <div className="section-content">{sections.startup_recommendations || "Не найдено"}</div>
        </div>        
        <button 
          onClick={() => setActiveTab('plan')}
          className="reset-button"
        >
          Вернуться к бизнес-плану
        </button>
      </div>
    );
  };  
  const renderPitchDeck = () => {
    if (!pitchDeck || !pitchDeck.pitch_deck) return null;    
    const slides = {
      title: extractSection(pitchDeck.pitch_deck, "## СЛАЙД 1: ЗАГЛАВНЫЙ СЛАЙД", "## СЛАЙД 2."),
      problem: extractSection(pitchDeck.pitch_deck, "## СЛАЙД 2: ПРОБЛЕМА", "## СЛАЙД 3."),
      solution: extractSection(pitchDeck.pitch_deck, "## СЛАЙД 3: РЕШЕНИЕ", "## СЛАЙД 4."),
      market: extractSection(pitchDeck.pitch_deck, "## СЛАЙД 4: РЫНОК", "## СЛАЙД 5."),
      business_model: extractSection(pitchDeck.pitch_deck, "## СЛАЙД 5: БИЗНЕС-МОДЕЛЬ", "## СЛАЙД 6."),
      competitors: extractSection(pitchDeck.pitch_deck, "## СЛАЙД 6: КОНКУРЕНТЫ", "## СЛАЙД 7."),
      team: extractSection(pitchDeck.pitch_deck, "## СЛАЙД 7: КОМАНДА", "## СЛАЙД 8."),
      finances: extractSection(pitchDeck.pitch_deck, "## СЛАЙД 8: ФИНАНСЫ", "## СЛАЙД 9."),
      action_plan: extractSection(pitchDeck.pitch_deck, "## СЛАЙД 9: ПЛАН ДЕЙСТВИЙ", "## СЛАЙД 10."),
      conclusion: extractSection(pitchDeck.pitch_deck, "## СЛАЙД 10: ЗАКЛЮЧЕНИЕ", null)
    };    
    return (
      <div className="pitch-deck">
        <h3>Pitch-дек для инвесторов</h3>        
        <div className="section">
          <h4>Слайд 1: Заглавный слайд</h4>
          <div className="section-content">{slides.title || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>Слайд 2: Проблема</h4>
          <div className="section-content">{slides.problem || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>Слайд 3: Решение</h4>
          <div className="section-content">{slides.solution || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>Слайд 4: Рынок</h4>
          <div className="section-content">{slides.market || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>Слайд 5: Бизнес-модель</h4>
          <div className="section-content">{slides.business_model || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>Слайд 6: Конкуренты</h4>
          <div className="section-content">{slides.competitors || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>Слайд 7: Команда</h4>
          <div className="section-content">{slides.team || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>Слайд 8: Финансы</h4>
          <div className="section-content">{slides.finances || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>Слайд 9: План действий</h4>
          <div className="section-content">{slides.action_plan || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>Слайд 10: Заключение</h4>
          <div className="section-content">{slides.conclusion || "Не найдено"}</div>
        </div>        
        <button 
          onClick={() => setActiveTab('plan')}
          className="reset-button"
        >
          Вернуться к бизнес-плану
        </button>
      </div>
    );
  };  
  const extractSection = (text: string, startMarker: string, endMarker: string | null): string => {
    const normalizeText = (str: string) => str.toLowerCase().replace(/\s+/g, ' ').trim();
    let startIndex = -1;
    const normalizedText = normalizeText(text);
    const normalizedStartMarker = normalizeText(startMarker);
    for (let i = 0; i < text.length - normalizedStartMarker.length; i++) {
      const segment = normalizeText(text.substring(i, i + normalizedStartMarker.length + 10));
      if (segment.includes(normalizedStartMarker)) {
        startIndex = i;
        break;
      }
    }
    if (startIndex === -1) return "";
    let endIndex = -1;
    if (endMarker) {
      const normalizedEndMarker = normalizeText(endMarker);
      for (let i = startIndex + startMarker.length; i < text.length - normalizedEndMarker.length; i++) {
        const segment = normalizeText(text.substring(i, i + normalizedEndMarker.length + 10));
        if (segment.includes(normalizedEndMarker)) {
          endIndex = i;
          break;
        }
      }
    }
    if (endIndex === -1) {
      return text.substring(startIndex + startMarker.length).trim();
    }
    return text.substring(startIndex + startMarker.length, endIndex).trim();
  };
  return (
    <div className="business-plan-container">
      <h2>Генерация бизнес-планов</h2>
      <p>Создавайте полные бизнес-планы, отраслевые шаблоны и pitch-деки для инвесторов</p>      
      <div className="tabs">
        <button 
          className={activeTab === 'plan' ? 'tab-active' : ''}
          onClick={() => setActiveTab('plan')}
        >
          Бизнес-план
        </button>
        <button 
          className={activeTab === 'template' ? 'tab-active' : ''}
          onClick={() => setActiveTab('template')}
        >
          Отраслевой шаблон
        </button>
        <button 
          className={activeTab === 'pitch' ? 'tab-active' : ''}
          onClick={() => setActiveTab('pitch')}
        >
          Pitch-дек
        </button>
      </div>      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}      
      {activeTab === 'plan' && (
        <form onSubmit={handleSubmit} className="business-plan-form">
          <div className="form-group">
            <label htmlFor="idea">Идея бизнеса *</label>
            <textarea
              id="idea"
              name="idea"
              value={formData.idea}
              onChange={handleChange}
              placeholder="Опишите идею вашего бизнеса"
              rows={4}
              required
            />
          </div>          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="type">Тип бизнеса</label>
              <select
                id="type"
                name="type"
                value={formData.type}
                onChange={handleChange}
              >
                <option value="стартап">Стартап</option>
                <option value="франшиза">Франшиза</option>
                <option value="малый бизнес">Малый бизнес</option>
                <option value="средний бизнес">Средний бизнес</option>
                <option value="крупный бизнес">Крупный бизнес</option>
              </select>
            </div>            
            <div className="form-group">
              <label htmlFor="country">Страна</label>
              <input
                type="text"
                id="country"
                name="country"
                value={formData.country}
                onChange={handleChange}
                placeholder="Например: Россия"
              />
            </div>
          </div>          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="target_market">Целевой рынок</label>
              <input
                type="text"
                id="target_market"
                name="target_market"
                value={formData.target_market}
                onChange={handleChange}
                placeholder="Например: локальный рынок"
              />
            </div>            
            <div className="form-group">
              <label htmlFor="investment_amount">Сумма инвестиций</label>
              <input
                type="text"
                id="investment_amount"
                name="investment_amount"
                value={formData.investment_amount}
                onChange={handleChange}
                placeholder="Например: средние инвестиции"
              />
            </div>
          </div>          
          <div className="form-group">
            <label htmlFor="timeframe">Горизонт планирования</label>
            <input
              type="text"
              id="timeframe"
              name="timeframe"
              value={formData.timeframe}
              onChange={handleChange}
              placeholder="Например: 3 года"
            />
          </div>          
          <button 
            type="submit" 
            className="generate-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Генерируем бизнес-план...
              </>
            ) : (
              'Сгенерировать бизнес-план'
            )}
          </button>
        </form>
      )}      
      {activeTab === 'template' && (
        <form onSubmit={handleSubmit} className="industry-template-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="industry">Отрасль *</label>
              <input
                type="text"
                id="industry"
                name="industry"
                value={industryData.industry}
                onChange={handleChange}
                placeholder="Например: IT, рестораны, образование"
                required
              />
            </div>            
            <div className="form-group">
              <label htmlFor="niche">Ниша</label>
              <input
                type="text"
                id="niche"
                name="niche"
                value={industryData.niche}
                onChange={handleChange}
                placeholder="Например: онлайн-образование для детей"
              />
            </div>
          </div>          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="business_model">Бизнес-модель</label>
              <select
                id="business_model"
                name="business_model"
                value={industryData.business_model}
                onChange={handleChange}
              >
                <option value="B2C">B2C (бизнес для потребителей)</option>
                <option value="B2B">B2B (бизнес для бизнеса)</option>
                <option value="B2B2C">B2B2C</option>
                <option value="C2C">C2C</option>
              </select>
            </div>            
            <div className="form-group">
              <label htmlFor="country">Страна</label>
              <input
                type="text"
                id="country"
                name="country"
                value={industryData.country}
                onChange={handleChange}
                placeholder="Например: Россия"
              />
            </div>
          </div>          
          <button 
            type="submit" 
            className="generate-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Генерируем отраслевой шаблон...
              </>
            ) : (
              'Сгенерировать отраслевой шаблон'
            )}
          </button>
        </form>
      )}      
      {activeTab === 'pitch' && (
        <form onSubmit={handleSubmit} className="pitch-deck-form">
          <div className="form-group">
            <label>Бизнес-план</label>
            <div className="business-plan-preview">
              {pitchData.business_plan ? (
                <div>
                  <p><strong>Идея:</strong> {formData.idea}</p>
                  <p><strong>Тип бизнеса:</strong> {formData.type}</p>
                </div>
              ) : (
                <p>Сначала сгенерируйте бизнес-план</p>
              )}
            </div>
          </div>          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="target_investors">Целевые инвесторы</label>
              <input
                type="text"
                id="target_investors"
                name="target_investors"
                value={pitchData.target_investors}
                onChange={handleChange}
                placeholder="Например: венчурные инвесторы"
              />
            </div>            
            <div className="form-group">
              <label htmlFor="presentation_time">Время презентации</label>
              <input
                type="text"
                id="presentation_time"
                name="presentation_time"
                value={pitchData.presentation_time}
                onChange={handleChange}
                placeholder="Например: 5-7 минут"
              />
            </div>
          </div>          
          <div className="form-group">
            <label htmlFor="country">Страна</label>
            <input
              type="text"
              id="country"
              name="country"
              value={pitchData.country}
              onChange={handleChange}
              placeholder="Например: Россия"
            />
          </div>          
          <button 
            type="submit" 
            className="generate-button"
            disabled={isLoading || !pitchData.business_plan}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Генерируем pitch-дек...
              </>
            ) : (
              'Сгенерировать pitch-дек'
            )}
          </button>
        </form>
      )}      
      {activeTab === 'plan' && result && renderBusinessPlan()}
      {activeTab === 'template' && industryTemplate && renderIndustryTemplate()}
      {activeTab === 'pitch' && pitchDeck && renderPitchDeck()}      
      <div className="footer-note">
        Советница АКВИ создает профессиональные бизнес-планы, отраслевые шаблоны и pitch-деки с использованием передовых моделей искусственного интеллекта. 
        Результаты носят рекомендательный характер и могут быть адаптированы под ваши потребности.
      </div>
    </div>
  );
};

export default BusinessPlanForm;