import React, { useState } from 'react';
import axios from 'axios';

interface Message {
    user: string;
    bot: string;
}

function Chat() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState<string>('');
    const handleSendMessage = async () => {
        if (!input.trim()) return;
        setMessages((prev) => [...prev, { user: input, bot: '' }]);
        try {
            const response = await axios.post(
                'https://advice-project.onrender.com/chat/',
                { message: input },
                { headers: { 'Content-Type': 'application/json' } }
            );
            const botReply = response.data.response || 'Неверный формат ответа';
            setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1].bot = botReply;
                return updated;
            });
        } catch (error: any) {
            console.error('Ошибка:', error.response?.data || error.message);
            setMessages((prev) => [...prev, { user: input, bot: 'Произошла ошибка...'}]);
        }
        setInput('');
    };
    return (
        <div className="chat-container">
            <h2>Поговори с АКВИ</h2>
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