import React, { useState } from 'react';
import 'jspdf';
import 'jspdf-autotable';

const BusinessPlanForm = () => {
  const [formData, setFormData] = useState({
    idea: '',
    type: 'стартап',
    country: 'Россия',
    target_market: 'локальный рынок',
    investment_amount: 'средние инвестиции',
    timeframe: '3 года'
  });
  
  // Добавлены недостающие состояния
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [financialAnalysis, setFinancialAnalysis] = useState<any>(null);
  const [marketingStrategy, setMarketingStrategy] = useState<any>(null);
  const [riskAnalysis, setRiskAnalysis] = useState<any>(null);
  const [actionPlan, setActionPlan] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'plan' | 'financial' | 'marketing' | 'risk' | 'action'>('plan');
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };  
  
  const handleCalculateFinancialPlan = async (businessPlan: string) => {
    if (!businessPlan || businessPlan.trim().length < 100) {
      setError('Недостаточно данных в бизнес-плане для расчета. Сначала сгенерируйте полный бизнес-план.');
      return;
    }
    setIsLoading(true);
    setError(null);    
    try {
      const response = await fetch('/business-plan/calculate-financial-plan/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          business_plan: businessPlan
        })
      });      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Ошибка при расчете финансового плана');
      }      
      const data = await response.json();
      setFinancialAnalysis(data);
      setActiveTab('financial');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleGenerateMarketingStrategy = async (businessPlan: string) => {
    if (!businessPlan || businessPlan.trim().length < 100) {
      setError('Недостаточно данных в бизнес-плане для генерации. Сначала сгенерируйте полный бизнес-план.');
      return;
    }    
    setIsLoading(true);
    setError(null);    
    try {
      const response = await fetch('/business-plan/generate-marketing-strategy/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          business_plan: businessPlan
        })
      });      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Ошибка при генерации маркетинговой стратегии');
      }      
      const data = await response.json();
      setMarketingStrategy(data);
      setActiveTab('marketing');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleGenerateRiskAnalysis = async (businessPlan: string) => {
    if (!businessPlan || businessPlan.trim().length < 100) {
      setError('Недостаточно данных в бизнес-плане для анализа. Сначала сгенерируйте полный бизнес-план.');
      return;
    }    
    setIsLoading(true);
    setError(null);    
    try {
      const response = await fetch('/business-plan/generate-risk-analysis/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          business_plan: businessPlan
        })
      });      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Ошибка при анализе рисков');
      }      
      const data = await response.json();
      setRiskAnalysis(data);
      setActiveTab('risk');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleGenerateActionPlan = async (businessPlan: string) => {
    if (!businessPlan || businessPlan.trim().length < 100) {
      setError('Недостаточно данных в бизнес-плане для генерации. Сначала сгенерируйте полный бизнес-план.');
      return;
    }    
    setIsLoading(true);
    setError(null);    
    try {
      const response = await fetch('/business-plan/generate-action-plan/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          business_plan: businessPlan
        })
      });      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Ошибка при генерации плана действий');
      }      
      const data = await response.json();
      setActionPlan(data);
      setActiveTab('action');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка');
    } finally {
      setIsLoading(false);
    }
  };
  
  const downloadPDF = async (content: string) => {
    setIsLoading(true);
    setError(null);    
    try {
      const { jsPDF } = await import('jspdf');
      await import('jspdf-autotable');
      
      const doc = new jsPDF();           
      doc.setFontSize(16);
      doc.text('Бизнес-план', 14, 20);
      doc.setFontSize(12);      
      const splitContent = doc.splitTextToSize(content, 180);
      doc.text(splitContent, 14, 30);      
      doc.save('business-plan.pdf');
    } catch (err) {
      setError('Не удалось сгенерировать PDF. Попробуйте позже.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();    
    setIsLoading(true);
    setError(null);    
    try {
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
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка');
    } finally {
      setIsLoading(false);
    }
  };
  
  const renderBusinessPlan = () => {
    if (!result || !result.business_plan) return null;    
    const sections = {
      executive_summary: extractSection(result.business_plan, 1, "ИСПОЛНИТЕЛЬНОЕ РЕЗЮМЕ"),
      business_description: extractSection(result.business_plan, 2, "ОПИСАНИЕ БИЗНЕСА"),
      market_analysis: extractSection(result.business_plan, 3, "АНАЛИЗ РЫНКА"),
      swot: extractSection(result.business_plan, 4, "SWOT-АНАЛИЗ"),
      competitor_analysis: extractSection(result.business_plan, 5, "КОНКУРЕНТНЫЙ АНАЛИЗ"),
      marketing_strategy: extractSection(result.business_plan, 6, "МАРКЕТИНГОВАЯ СТРАТЕГИЯ"),
      operations_plan: extractSection(result.business_plan, 7, "ПЛАН ОПЕРАЦИЙ"),
      organizational_structure: extractSection(result.business_plan, 8, "ОРГАНИЗАЦИОННАЯ СТРУКТУРА"),
      financial_plan: extractSection(result.business_plan, 9, "ФИНАНСОВЫЙ ПЛАН"),
      risks: extractSection(result.business_plan, 10, "РИСКИ И ИХ МИНИМИЗАЦИЯ")
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
      </div>
    );
  };
  
  const renderFinancialAnalysis = () => {
    if (!financialAnalysis || !financialAnalysis.financial_analysis) return null;      
    const sections = {
      investment_plan: extractSection(financialAnalysis.financial_analysis, 1, "1. ИНВЕСТИЦИОННЫЙ ПЛАН"),
      revenue_forecast: extractSection(financialAnalysis.financial_analysis, 2, "2. ПРОГНОЗ ДОХОДОВ"),
      expense_forecast: extractSection(financialAnalysis.financial_analysis, 3, "3. ПРОГНОЗ РАСХОДОВ"),
      break_even: extractSection(financialAnalysis.financial_analysis, 4, "4. ТОЧКА БЕЗУБЫТОЧНОСТИ"),
      profit_forecast: extractSection(financialAnalysis.financial_analysis, 5, "5. ПРОГНОЗ ПРИБЫЛИ"),
      scenario_analysis: extractSection(financialAnalysis.financial_analysis, 6, "6. СЦЕНАРНЫЙ АНАЛИЗ"),
      optimization_recommendations: extractSection(financialAnalysis.financial_analysis, 7, "7. РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ")
    };    
    return (
      <div className="financial-analysis">
        <h3>Детальный финансовый анализ</h3>        
        <div className="section">
          <h4>1. Инвестиционный план</h4>
          <div className="section-content">{sections.investment_plan || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>2. Прогноз доходов</h4>
          <div className="section-content">{sections.revenue_forecast || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>3. Прогноз расходов</h4>
          <div className="section-content">{sections.expense_forecast || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>4. Точка безубыточности</h4>
          <div className="section-content">{sections.break_even || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>5. Прогноз прибыли</h4>
          <div className="section-content">{sections.profit_forecast || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>6. Сценарный анализ</h4>
          <div className="section-content">{sections.scenario_analysis || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>7. Рекомендации по оптимизации</h4>
          <div className="section-content">{sections.optimization_recommendations || "Не найдено"}</div>
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
  
  const renderMarketingStrategy = () => {
    if (!marketingStrategy || !marketingStrategy.marketing_strategy) return null;    
    const sections = {
      target_audience: extractSection(marketingStrategy.marketing_strategy, 1, "1. ЦЕЛЕВАЯ АУДИТОРИЯ"),
      utp_positioning: extractSection(marketingStrategy.marketing_strategy, 2, "2. УТП И ПОЗИЦИОНИРОВАНИЕ"),
      pricing_strategy: extractSection(marketingStrategy.marketing_strategy, 3, "3. ЦЕННАЯ СТРАТЕГИЯ"),
      promotion_channels: extractSection(marketingStrategy.marketing_strategy, 4, "4. КАНАЛЫ ПРОДВИЖЕНИЯ"),
      content_strategy: extractSection(marketingStrategy.marketing_strategy, 5, "5. КОНТЕНТ-СТРАТЕГИЯ"),
      sales_conversion: extractSection(marketingStrategy.marketing_strategy, 6, "6. ПРОДАЖИ И КОНВЕРСИЯ"),
      effectiveness_measurement: extractSection(marketingStrategy.marketing_strategy, 7, "7. ИЗМЕРЕНИЕ ЭФФЕКТИВНОСТИ"),
      marketing_budget: extractSection(marketingStrategy.marketing_strategy, 8, "8. БЮДЖЕТ МАРКЕТИНГА")
    };    
    return (
      <div className="marketing-strategy">
        <h3>Детальная маркетинговая стратегия</h3>        
        <div className="section">
          <h4>1. Целевая аудитория</h4>
          <div className="section-content">{sections.target_audience || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>2. УТП и позиционирование</h4>
          <div className="section-content">{sections.utp_positioning || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>3. Ценная стратегия</h4>
          <div className="section-content">{sections.pricing_strategy || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>4. Каналы продвижения</h4>
          <div className="section-content">{sections.promotion_channels || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>5. Контент-стратегия</h4>
          <div className="section-content">{sections.content_strategy || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>6. Продажи и конверсия</h4>
          <div className="section-content">{sections.sales_conversion || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>7. Измерение эффективности</h4>
          <div className="section-content">{sections.effectiveness_measurement || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>8. Бюджет маркетинга</h4>
          <div className="section-content">{sections.marketing_budget || "Не найдено"}</div>
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
  
  const renderRiskAnalysis = () => {
    if (!riskAnalysis || !riskAnalysis.risk_analysis) return null;    
    const sections = {
      risk_identification: extractSection(riskAnalysis.risk_analysis, 1, "1. ИДЕНТИФИКАЦИЯ РИСКОВ"),
      risk_assessment: extractSection(riskAnalysis.risk_analysis, 2, "2. ОЦЕНКА РИСКОВ"),
      risk_map: extractSection(riskAnalysis.risk_analysis, 3, "3. КАРТА РИСКОВ"),
      mitigation_plans: extractSection(riskAnalysis.risk_analysis, 4, "4. ПЛАНЫ МИНИМИЗАЦИИ"),
      risk_monitoring: extractSection(riskAnalysis.risk_analysis, 5, "5. МОНИТОРИНГ РИСКОВ"),
      scenario_planning: extractSection(riskAnalysis.risk_analysis, 6, "6. СЦЕНАРИЙНОЕ ПЛАНИРОВАНИЕ"),
      risk_insurance: extractSection(riskAnalysis.risk_analysis, 7, "7. СТРАХОВАНИЕ РИСКОВ"),
      recommendations: extractSection(riskAnalysis.risk_analysis, 8, "8. РЕЗЮМЕ И РЕКОМЕНДАЦИИ")
    };    
    return (
      <div className="risk-analysis">
        <h3>Глубокий анализ рисков</h3>        
        <div className="section">
          <h4>1. Идентификация рисков</h4>
          <div className="section-content">{sections.risk_identification || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>2. Оценка рисков</h4>
          <div className="section-content">{sections.risk_assessment || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>3. Карта рисков</h4>
          <div className="section-content">{sections.risk_map || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>4. Планы минимизации</h4>
          <div className="section-content">{sections.mitigation_plans || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>5. Мониторинг рисков</h4>
          <div className="section-content">{sections.risk_monitoring || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>6. Сценарийное планирование</h4>
          <div className="section-content">{sections.scenario_planning || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>7. Страхование рисков</h4>
          <div className="section-content">{sections.risk_insurance || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>8. Резюме и рекомендации</h4>
          <div className="section-content">{sections.recommendations || "Не найдено"}</div>
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
  
  const renderActionPlan = () => {
    if (!actionPlan || !actionPlan.action_plan) return null;    
    const sections = {
      project_phases: extractSection(actionPlan.action_plan, 1, "1. КЛЮЧЕВЫЕ ЭТАПЫ ПРОЕКТА"),
      work_schedule: extractSection(actionPlan.action_plan, 2, "2. ДЕТАЛЬНЫЙ ГРАФИК РАБОТ"),
      resource_provision: extractSection(actionPlan.action_plan, 3, "3. РЕСУРСНОЕ ОБЕСПЕЧЕНИЕ"),
      responsible: extractSection(actionPlan.action_plan, 4, "4. ОТВЕТСТВЕННЫЕ"),
      success_criteria: extractSection(actionPlan.action_plan, 5, "5. КРИТЕРИИ УСПЕХА"),
      budget_by_stages: extractSection(actionPlan.action_plan, 6, "6. БЮДЖЕТ ПО ЭТАПАМ"),
      potential_problems: extractSection(actionPlan.action_plan, 7, "7. ПОТЕНЦИАЛЬНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ"),
      monitoring_system: extractSection(actionPlan.action_plan, 8, "8. СИСТЕМА МОНИТОРИНГА И ОТЧЕТНОСТИ")
    };    
    return (
      <div className="action-plan">
        <h3>Детальный план действий</h3>        
        <div className="section">
          <h4>1. Ключевые этапы проекта</h4>
          <div className="section-content">{sections.project_phases || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>2. Детальный график работ</h4>
          <div className="section-content">{sections.work_schedule || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>3. Ресурсное обеспечение</h4>
          <div className="section-content">{sections.resource_provision || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>4. Ответственные</h4>
          <div className="section-content">{sections.responsible || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>5. Критерии успеха</h4>
          <div className="section-content">{sections.success_criteria || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>6. Бюджет по этапам</h4>
          <div className="section-content">{sections.budget_by_stages || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>7. Потенциальные проблемы и решения</h4>
          <div className="section-content">{sections.potential_problems || "Не найдено"}</div>
        </div>        
        <div className="section">
          <h4>8. Система мониторинга и отчетности</h4>
          <div className="section-content">{sections.monitoring_system || "Не найдено"}</div>
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
  
  const extractSection = (text: string, sectionNumber: number, sectionTitle: string): string => {
    if (!text) return "Не найдено";
    const patterns = [
      new RegExp(`^\\s*${sectionNumber}\\.\\s*${sectionTitle}\\s*\\n`, 'i'),
      new RegExp(`^\\s*${sectionNumber}\\.\\s*${sectionTitle.substring(0, 5)}`, 'i'),
      new RegExp(`\\s*${sectionNumber}\\.\\s*${sectionTitle}\\s*\\n`, 'i'),
      new RegExp(`\\s*${sectionNumber}\\.\\s*${sectionTitle.substring(0, 5)}`, 'i')
    ];
    let startIndex = -1;
    //let patternUsed = '';
    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match && match.index !== undefined) {
        startIndex = match.index + match[0].length;
        //patternUsed = pattern.toString();
        break;
      }
    }
    if (startIndex === -1) return "Не найдено";
    let endIndex = text.length;
    for (let i = sectionNumber + 1; i <= 10; i++) {
      const nextSectionPatterns = [
        new RegExp(`\\s*${i}\\.`, 'i'),
        new RegExp(`^\\s*${i}\\.`, 'i')
      ];  
      for (const nextPattern of nextSectionPatterns) {
        const nextMatch = text.substring(startIndex).match(nextPattern);
        if (nextMatch && nextMatch.index !== undefined) {
          endIndex = startIndex + nextMatch.index;
          break;
        }
      }    
      if (endIndex < text.length) break;
    }
    let content = text.substring(startIndex, endIndex).trim();
    const endingPatterns = [
      new RegExp(`\\s*\\d+\\.\\s*[А-Яа-я]+\\s*$`),
      new RegExp(`\\s*\\d+\\.\\s*$`)
    ];
    for (const endingPattern of endingPatterns) {
      content = content.replace(endingPattern, '').trim();
    }
    return content || "Не найдено";
  };
  
  return (
    <div className="business-plan-container">
      <h2>Генерация бизнес-планов</h2>
      <p>Создавайте полные бизнес-планы для инвесторов</p>      
      <div className="tabs">
        <button 
          className={activeTab === 'plan' ? 'tab-active' : ''}
          onClick={() => setActiveTab('plan')}
        >
          Бизнес-план
        </button>
        <button 
          className={activeTab === 'financial' ? 'tab-active' : ''}
          onClick={() => setActiveTab('financial')}
        >
          Финансовый анализ
        </button>
        <button 
          className={activeTab === 'marketing' ? 'tab-active' : ''}
          onClick={() => setActiveTab('marketing')}
        >
          Маркетинговая стратегия
        </button>
        <button 
          className={activeTab === 'risk' ? 'tab-active' : ''}
          onClick={() => setActiveTab('risk')}
        >
          Анализ рисков
        </button>
        <button 
          className={activeTab === 'action' ? 'tab-active' : ''}
          onClick={() => setActiveTab('action')}
        >
          План действий
        </button>
      </div>      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}      
      {activeTab === 'plan' && !result && (
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
      
      {activeTab === 'plan' && result && (
        <>
          {renderBusinessPlan()}
          <div className="button-group">
            <button 
              onClick={() => handleCalculateFinancialPlan(result.business_plan)}
              className="generate-button"
              disabled={isLoading}
            >
              {isLoading ? 'Рассчитываем финансовый план...' : 'Рассчитать финансовый план'}
            </button>          
            <button 
              onClick={() => handleGenerateMarketingStrategy(result.business_plan)}
              className="generate-button"
              disabled={isLoading}
            >
              {isLoading ? 'Генерируем маркетинговую стратегию...' : 'Генерировать маркетинговую стратегию'}
            </button>          
            <button 
              onClick={() => handleGenerateRiskAnalysis(result.business_plan)}
              className="generate-button"
              disabled={isLoading}
            >
              {isLoading ? 'Анализируем риски...' : 'Анализ рисков'}
            </button>          
            <button 
              onClick={() => handleGenerateActionPlan(result.business_plan)}
              className="generate-button"
              disabled={isLoading}
            >
              {isLoading ? 'Генерируем план действий...' : 'План действий'}
            </button>          
            <button 
              onClick={() => downloadPDF(result.business_plan)}
              className="download-button"
              disabled={isLoading}
            >
              Скачать PDF
            </button>
          </div>
        </>
      )}
      
      {activeTab === 'financial' && financialAnalysis && renderFinancialAnalysis()}
      {activeTab === 'marketing' && marketingStrategy && renderMarketingStrategy()}
      {activeTab === 'risk' && riskAnalysis && renderRiskAnalysis()}
      {activeTab === 'action' && actionPlan && renderActionPlan()}     
      
      <div className="footer-note">
        Советница АКВИ создает профессиональные бизнес-планы с использованием передовых моделей искусственного интеллекта. 
        Результаты носят рекомендательный характер и могут быть адаптированы под ваши потребности.
      </div>
    </div>
  );
};

export default BusinessPlanForm;