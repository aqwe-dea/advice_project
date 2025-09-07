import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { styled } from 'styled-components';

const ChatContainer = styled.div`
         max-width: 600px;
         margin: 40px auto;
         padding: 24px;
         background: #F5F5DC;
         border-radius: 16px;
`;

const userMessageStyle = {
    backgroundColor: '#3498db',
    color: 'white',
    marginLeft: 'auto',
    borderRadius: '12px 12px 0 12px',
    padding: '0.8rem 1rem',
    maxWidth: '80%',
    marginBottom: '1rem'
  };

const aquaMessageStyle = {
  backgroundColor: '#2c3e50',
  color: 'white', // Это решит проблему с белым текстом
  marginRight: 'auto',
  borderRadius: '12px 12px 12px 0',
  padding: '0.8rem 1rem',
  maxWidth: '80%',
  marginBottom: '1rem'
};

interface HuggingFaceResponse {
    choices: Array<{
        message: {
            content: string;
        };
    }>;
    response: string;
}

interface Message {
    user: string;
    bot: string;
}

function Chat() {
    useEffect(() => {
        const fetchHistory = async () => {
            const history = await axios.get('/api/user-history/?email=...');
            setMessages(history.data.map((msg: any) => ({
                user: msg.question,
                bot: msg.answer
            })));
    };
    fetchHistory();
    }, []);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState<string>('');
    const [error, setError] = useState<string | null>(null);
    const handleSendMessage = async () => {
        if (!input.trim()) return;
        setMessages((prev) => [...prev, { user: input, bot: '' }]);
        try {
            const response = await axios.post<HuggingFaceResponse>(
                '/chat/',
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
        <ChatContainer>
        <motion.div
         initial={{ y: 20, opacity: 0 }}
         animate={{ y: 0, opacity: 1 }}
         transition={{ duration: 0.5 }}
        >
        <div style={message.sender === 'user' ? userMessageStyle : aquaMessageStyle}>
        {message.text}
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
        </div>
        </motion.div>
        </ChatContainer>
    );
}

export default Chat;