import React from 'react';

//export const PersonalizedModule: React.FC<ModuleProps> = ({ topic, level, modalities }) => {
    // Один компонент генерирует всё на основе пропсов
//    return (); 
//};

interface ModuleProps {
    topic: string;
    level: 'beginner' | 'intermediate' | 'advanced';
    modalities: ('text' | 'image' | 'audio' | 'interactive')[];
}