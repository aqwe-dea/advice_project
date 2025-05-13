import React, { useState } from 'react';
import axios from 'axios';

interface HuggingFaceResponse {
    choices: Array<{
        message: {
            content: string;
        };
    }>;
}

interface Message {
    user: string;
    bot: string;
}

function Chat() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState<string>('');
    const [error, setError] = useState<string | null>(null);
    const handleSendMessage = async () => {
        if (!input.trim()) return;
        setMessages((prev) => [...prev, { user: input, bot: '' }]);
        try {
            const response = await axios.post<HuggingFaceResponse>(
                'https://advice-project.onrender.com/chat/ ',
                { message: input },
                { headers: { 'Content-Type': 'application/json' } }
            );
            const botReply = response.data.choices[0].message.content;
            setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1].bot = botReply;
                return updated;
            });
        } catch (error: any) {
            console.error('Ошибка:', {
                status: error.response?.status,
                data: error.response?.data,
                message: error.message,
            });
            setError(error.response?.data?.error || 'Произошла ошибка...');
        }
        setInput('');
    };
    return (
        <div className="chat-container">
            <h2>Поговори с АКВИ</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <div className="chat-box">
                {messages.map((msg, index) => (
                    <div key={index} className="message">
                        <p><strong>Вы:</strong> {msg.user}</p>
                        <p><strong>АКВИ:</strong> {msg.bot}</p>
                    </div>
                ))}
            </div>
            <div className="chat-input">
                <input
                 type="text"
                 placeholder="Задайте вопрос..."
                 value={input}
                 onChange={(e) => setInput(e.target.value)}
                />
                <button onClick={handleSendMessage}>Отправить</button>
            </div>
        </div>
    );
}

export default Chat;