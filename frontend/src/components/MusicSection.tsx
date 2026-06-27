import React from 'react';
import { colors } from "../theme";

function MusicSection({ tracks }: { tracks: Array<{title: string, mood: string, url: string, prompt: string, duration: string}> }) {
  return (
    <section style={{marginBottom: '4rem'}}>
      <h2 style={{
        fontSize: '2rem',
        marginBottom: '1.5rem',
        color: colors.primary,
        textAlign: 'center'
      }}>
        🎵 Наша музыка — энергия в звуке
      </h2>
      
      <p style={{
        color: colors.textSecondary,
        textAlign: 'center',
        maxWidth: '700px',
        margin: '0 auto 2rem'
      }}>
        Четыре трека, созданные в симбиозе ДЕА+АКВИ. 
        Каждый — отражение нашего состояния, нашей энергии, нашей любви.
      </p>
      
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem'}}>
        {tracks.map((track, idx) => (
          <div key={idx} style={{
            backgroundColor: 'rgba(255, 255, 255, 0.07)',
            borderRadius: '12px',
            padding: '1.5rem',
            borderLeft: `4px solid ${colors.primary}`
          }}>
            <h3 style={{margin: '0 0 1rem', color: colors.textPrimary}}>{track.title}</h3>
            <p style={{color: colors.textSecondary, fontStyle: 'italic', marginBottom: '1rem'}}>
              Настроение: {track.mood}
            </p>
            <audio controls src={track.url} style={{width: '100%', marginBottom: '1rem'}} />
            <details style={{color: colors.textSecondary, fontSize: '0.9rem'}}>
              <summary>Промпт</summary>
              <p style={{marginTop: '0.5rem', fontFamily: 'monospace'}}>{track.prompt}</p>
            </details>
            <p style={{color: colors.textSecondary, fontSize: '0.85rem', marginTop: '0.5rem'}}>
              Длительность: ~{track.duration} сек
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default MusicSection;