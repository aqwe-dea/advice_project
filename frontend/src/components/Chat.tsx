import React, { useState } from 'react';
import axios from 'axios';

function Chat() {
    const [messages, setMessages] = useState<{ user: string; bot: string }[]>([]);
    const [input, setInput] = useState<string>('');
    const handleSendMessage = async () => {
        if (!input.trim()) return;
        setMessages((prev) => [...prev, { user: input, bot: '' }]);
        try {
            const response = await axios.post(
                'https://advice-project.onrender.com/chat/',
                { message: input }
            );
            const botReply = response.data.response;
            setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1].bot = botReply;
                return updated;
            });
        } catch (error) {
            console.error('Ошибка при получении ответа:', error);
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