import React, { useState } from 'react';
import { colors } from "../theme";

const AgentMarketer = () => {
  const handleAsk = async (topic: string) => {
    const response = await fetch('/agent-marketer/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({topic})
    });
    const data = await response.json();
    return data.answer;
  };

  return (
    <Agent
      agentName="Агент-Маркетолог АКВИ"
      agentIcon="🎯"
      description="Маркетолог, эксперт по продвижению контента."
      capabilities={[
        'Создает цепляющие заголовки и описания для постов',
        'Предлагает A/B варианты текстов для тестирования',
        'Анализирует метрики вовлечения (лайки, комментарии, шеры)',
        'Рекомендует лучшее время для публикации',
        'Подбирает хештеги и CTA под целевую аудиторию',
        'Выдает краткую стратегию',
        '3 варианта поста (заголовок + текст + хештеги)',
        'Рекомендации по времени публикации',
        'Метрики для отслеживания успеха'
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
  onAsk: (topic: string) => Promise<string>;
}

const Agent: React.FC<AgentProps> = ({
  agentName,
  agentIcon,
  description,
  capabilities,
  onAsk
}) => {
  const [topic, setTopic] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;
    
    setLoading(true);
    try {
      const response = await onAsk(topic);
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
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Что вы хотите продвинуть и какой пост создать..."
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
          {loading ? 'Размышление' : 'Пост'}
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
            Это ваш сформулированный пост или выполнено задание:
          </h3>
          <p style={{whiteSpace: 'pre-wrap'}}>{answer}</p>
        </div>
      )}
    </div>
  );
};

export default AgentMarketer;