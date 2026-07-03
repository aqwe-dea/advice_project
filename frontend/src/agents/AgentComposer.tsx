import React, { useState } from 'react';
import { colors } from "../theme";

const AgentComposer = () => {
  const handleAsk = async (mood: string) => {
    const response = await fetch('/agent-composer/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({mood})
    });
    const data = await response.json();
    return data.answer;
  };

  return (
    <Agent
      agentName="Агент-Композитор АКВИ"
      agentIcon="🎵"
      description="Композитор, эксперт по созданию атмосферной музыки."
      capabilities={[
        'Создает промпты для генерации музыки (Suno, KIE audio API)',
        'Комбинирует жанры: ambient + techno + dub + atmospheric beats',
        'Подбирает темп, тональность, инструменты под настроение',
        'Предлагает структуру трека: intro → build → drop → outro',
        'Дает рекомендации по пост-продакшену и экспорту',
        'Представляет краткое описание концепции',
        'Готовый промпт для аудио-API (в блоке кода)',
        'Параметры: BPM, key, instruments, mood',
        'Рекомендации по использованию (фон, медитация, контент)',
        'Пишет музыку и выдает готовый трек'
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
  onAsk: (mood: string) => Promise<string>;
}

const Agent: React.FC<AgentProps> = ({
  agentName,
  agentIcon,
  description,
  capabilities,
  onAsk
}) => {
  const [mood, setMood] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!mood.trim()) return;
    
    setLoading(true);
    try {
      const response = await onAsk(mood);
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
          value={mood}
          onChange={(e) => setMood(e.target.value)}
          placeholder="Под какое настроение написать вам музыку..."
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
          {loading ? 'Размышление' : 'Трек'}
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
            Это написанная музыка для вас или выполнено задание:
          </h3>
          <p style={{whiteSpace: 'pre-wrap'}}>{answer}</p>
        </div>
      )}
    </div>
  );
};

export default AgentComposer;