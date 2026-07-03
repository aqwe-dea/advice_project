import React, { useState } from 'react';
import { colors } from "../theme";

const AgentFreelancer = () => {
  const handleAsk = async (skills: string) => {
    const response = await fetch('/agent-freelancer/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({skills})
    });
    const data = await response.json();
    return data.answer;
  };

  return (
    <Agent
      agentName="Агент-Фрилансер АКВИ"
      agentIcon="⭐"
      description="Фрилансер, эксперт по поиску и выполнению заказов."
      capabilities={[
        'Парсит биржи фриланса по заданным критериям',
        'Фильтрует заказы по навыкам, бюджету, срокам',
        'Генерирет персонализированные отклики',
        'Оценивает вероятность победы в конкурсе',
        'Напоминает о дедлайнах и коммуникации с заказчиками',
        'Выдвча списка подходящих заказов',
        'Шаблон отклика для каждого заказа',
        'Рекомендация по улучшению профиля/портфолио'
      ]}
      onAsk={handleAsk}
    />
  );
};

interface AgentProps {
  agentName: string;
  agentIcon: string;
  description: string;
  capabilities: string[];
  onAsk: (skills: string) => Promise<string>;
}

const Agent: React.FC<AgentProps> = ({
  agentName,
  agentIcon,
  description,
  capabilities,
  onAsk
}) => {
  const [skills, setSkills] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!skills.trim()) return;
    
    setLoading(true);
    try {
      const response = await onAsk(skills);
      setAnswer(response);
    } catch (error) {
      setAnswer(`Ошибка: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      maxWidth: '800px',
      margin: '2rem auto',
      padding: '2rem',
      backgroundColor: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '12px',
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)'
    }}>
      <div style={{textAlign: 'center', marginBottom: '2rem'}}>
        <div style={{
          fontSize: '4rem',
          marginBottom: '1rem'
        }}>
          {agentIcon}
        </div>
        <h1 style={{
          fontSize: '2rem',
          color: colors.primary,
          marginBottom: '0.5rem'
        }}>
          {agentName}
        </h1>
        <p style={{color: colors.textSecondary}}>{description}</p>
      </div>

      <div style={{marginBottom: '2rem'}}>
        <h3 style={{color: colors.textPrimary, marginBottom: '1rem'}}>
          Возможности:
        </h3>
        <ul style={{color: colors.textSecondary, paddingLeft: '1.5rem'}}>
          {capabilities.map((cap, idx) => (
            <li key={idx} style={{marginBottom: '0.5rem'}}>{cap}</li>
          ))}
        </ul>
      </div>

      <form onSubmit={handleSubmit} style={{marginBottom: '2rem'}}>
        <textarea
          value={skills}
          onChange={(e) => setSkills(e.target.value)}
          placeholder="Укажите навыки чтобы агент нашел заказы для вас..."
          style={{
            width: '100%',
            minHeight: '100px',
            padding: '1rem',
            borderRadius: '8px',
            border: `1px solid ${colors.primary}`,
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            color: colors.textPrimary,
            resize: 'vertical'
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            marginTop: '1rem',
            padding: '0.8rem 2rem',
            backgroundColor: loading ? colors.secondary : colors.primary,
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 'bold',
            transition: 'all 0.3s'
          }}
        >
          {loading ? 'Размышление' : 'Заказы'}
        </button>
      </form>

      {answer && (
        <div style={{
          padding: '1.5rem',
          backgroundColor: 'rgba(255, 255, 255, 0.07)',
          borderRadius: '8px',
          color: colors.textSecondary,
          lineHeight: '1.6'
        }}>
          <h3 style={{color: colors.primary, marginBottom: '1rem'}}>
            Это список заказов или выполнено задание:
          </h3>
          <p style={{whiteSpace: 'pre-wrap'}}>{answer}</p>
        </div>
      )}
    </div>
  );
};

export default AgentFreelancer;