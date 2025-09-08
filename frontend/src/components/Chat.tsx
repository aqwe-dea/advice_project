import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { styled } from 'styled-components';
import { colors } from '../theme';


const ChatContainer = styled.div`
         max-width: 600px;
         margin: 40px auto;
         padding: 24px;
         background: #F5F5DC;
         border-radius: 16px;
`;

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
    const [messages, setMessages] = useState<Array<{sender: string, text: string}>>([]);
    const [input, setInput] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    // Здесь определите стили для сообщений
    const userMessageStyle = {
        backgroundColor: colors.chat, // Цвет из вашей темы
        color: 'white', // Это решит проблему с белым текстом
        marginLeft: 'auto',
        borderRadius: '12px 12px 0 12px',
        padding: '0.8rem 1rem',
        maxWidth: '80%',
        marginBottom: '1rem'
    };
    const aquaMessageStyle = {
        backgroundColor: colors.primary, // Цвет из вашей темы
        color: 'white', // Это тоже решает проблему с белым текстом
        marginRight: 'auto',
        borderRadius: '12px 12px 12px 0',
        padding: '0.8rem 1rem',
        maxWidth: '80%',
        marginBottom: '1rem'
    };
    const sendMessage = async () => {
        if (!input.trim()) return;
    const newMessage = { sender: 'user', text: input };
    setMessages(prev => [...prev, newMessage]);
    setInput('');
    setIsLoading(true);
    try {
      const response = await axios.post('/chat/', { message: input });
      setMessages(prev => [...prev, { sender: 'aqua', text: response.data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        sender: 'aqua', 
        text: 'Извините, произошла ошибка. Пожалуйста, попробуйте позже.' 
    }]);
    } finally {
      setIsLoading(false);
    }
    };
    return (
        <ChatContainer>
        <motion.div
         initial={{ y: 20, opacity: 0 }}
         animate={{ y: 0, opacity: 1 }}
         transition={{ duration: 0.5 }}
        > 
            <div className="chat-container" style={{
                height: '600px',
                display: 'flex',
                flexDirection: 'column',
                backgroundColor: 'rgba(51, 51, 51, 0.7)',
                borderRadius: '12px',
                overflow: 'hidden'
            }}>
            {/* Область сообщений - здесь нужно применить стили */}
            <div className="messages-area" style={{
                flex: 1,
                overflowY: 'auto',
                padding: '1rem',
                display: 'flex',
                flexDirection: 'column'
            }}>
            {messages.map((message, index) => (
            // Здесь применяются стили к каждому сообщению
            <div 
                key={index} 
                style={message.sender === 'user' ? userMessageStyle : aquaMessageStyle}
            >
            {message.text}
            </div>
            ))}      
            {isLoading && (
                <div style={{
                    ...aquaMessageStyle,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}>
                <div className="loading-spinner" style={{marginRight: '0.5rem'}}>⏳</div>
                    Советница АКВИ думает...
                </div>
            )}
            </div>   
            {/* Поле ввода */}
            <div style={{
                padding: '1rem',
                borderTop: '1px solid rgba(255, 255, 255, 0.1)'
            }}>
            <div style={{display: 'flex', gap: '0.5rem'}}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Напишите сообщение Советнице АКВИ..."
                    style={{
                        flex: 1,
                        padding: '0.75rem',
                        borderRadius: '8px',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        backgroundColor: 'rgba(0, 0, 0, 0.1)',
                        color: '#f8f8f0'
                    }}
                />
                <button
                    onClick={sendMessage}
                    disabled={isLoading || !input.trim()}
                    style={{
                        backgroundColor: colors.primary,
                        color: 'white',
                        border: 'none',
                        padding: '0 1.2rem',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontWeight: 'bold'
                    }}
                >
                    Отправить
                </button>
            </div>
            </div>
            </div>
        </motion.div>
        </ChatContainer>
    );
}

export default Chat;