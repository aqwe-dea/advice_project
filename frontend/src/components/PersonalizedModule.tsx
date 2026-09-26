import React from 'react';

export interface ModuleProps {
    topic: string;
    level: 'beginner' | 'intermediate' | 'advanced';
    modalities: ('text' | 'image' | 'audio' | 'interactive')[];
}

export const PersonalizedModule: React.FC<ModuleProps> = ({ topic, level, modalities }) => {
    return (
        <div className="p-4 border rounded-lg bg-purple-50 dark:bg-purple-900/20">
            <h3 className="text-xl font-bold mb-2">📚 {topic}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
                Уровень: <span className="font-semibold capitalize">{level}</span>
            </p>
            <div className="flex gap-2 flex-wrap">
                {modalities.map(mod => (
                    <span key={mod} className="px-3 py-1 bg-purple-200 dark:bg-purple-800 rounded-full text-xs font-medium">
                        {mod === 'text' && '📝 Текст'}
                        {mod === 'image' && '🖼️ Изображение'}
                        {mod === 'audio' && '🎧 Аудио'}
                        {mod === 'interactive' && '🎮 Интерактив'}
                    </span>
                ))}
            </div>
        </div>
    );
};