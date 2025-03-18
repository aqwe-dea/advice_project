import React from 'react';

interface AdviceCardProps {
advice: {
    category: string;
    question: string;
    answer: string;
};
}
function AdviceCard({ advice }: AdviceCardProps) {
    return (
        <div className="advice-card">
            <h3>{advice.category}</h3>
            <p><strong>Вопрос:</strong> {advice.question}</p>
            <p><strong>Ответ:</strong> {advice.answer}</p>
        </div>
    );
}

export default AdviceCard;