import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../App.css';
import { motion } from 'framer-motion';
import { styled } from 'styled-components';
import { colors } from '../theme';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://advice-project.onrender.com';

function AgentChatForm() {
    const [messages, setMessages] = useState<Array<{ sender: string; text: string }>>([]);
    const [input, setInput] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const userEmail = 'user@example.com';
                const response = await axios.get(`${API_BASE_URL}/api/user-history/?email=${userEmail}`);
                
                // ✅ Правильная обработка истории
                const historyMessages = response.data.map((msg: any) => [
                    { sender: 'user', text: msg.question },
                    { sender: 'aqwe', text: msg.answer }
                ]).flat();
                
                setMessages(historyMessages);
            } catch (err) {
                setError('Не удалось загрузить историю сообщений');
                console.error('Error fetching history:', err);
            }
        };
        fetchHistory();
    }, []);
    
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
    const aqweMessageStyle = {
        backgroundColor: colors.primary, // Цвет из вашей темы
        color: 'white', // Это тоже решает проблему с белым текстом
        marginRight: 'auto',
        borderRadius: '12px 12px 12px 0',
        padding: '0.8rem 1rem',
        maxWidth: '80%',
        marginBottom: '1rem'
    };
    const sendQuestion = async () => {
        if (!input.trim()) return;
        
        const newQuestion = { sender: 'user', text: input };
        setMessages(prev => [...prev, newQuestion]);
        setInput('');
        setIsLoading(true);
        setError(null);
        
        try {
            // ✅ Используем полный URL
            const response = await axios.post(
                '/agent-chat/', 
                { question: input },
                { timeout: 30000 }
            );
            
            setMessages(prev => [
                ...prev, 
                { sender: 'aqwe', text: response.data.answer }
            ]);
        } catch (error) {
            setError('Не удалось получить ответ от агента');
            console.error('Error agent message:', error);
            const errorMessage = 'Извините, произошла ошибка. Пожалуйста, попробуйте позже.';
            setMessages(prev => [
                ...prev, 
                { sender: 'aqwe', text: errorMessage }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <AgentContainer>
        <motion.div
         initial={{ y: 20, opacity: 0 }}
         animate={{ y: 0, opacity: 1 }}
         transition={{ duration: 0.5 }}
        > 
            <div className="Agent-Chat-Form" style={{
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
                <div 
                    key={index} 
                    style={message.sender === 'user' ? userMessageStyle : aqweMessageStyle}
                >
                    {message.text}
                </div>
            ))}      
            {isLoading && (
                <div style={{
                    ...aqweMessageStyle,
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
                    onKeyPress={(e) => e.key === 'Enter' && sendQuestion()}
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
                    onClick={sendQuestion}
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
        </AgentContainer>
    );
}

const AgentContainer = styled.div`
    max-width: 600px;
    margin: 40px auto;
    padding: 24px;
    background: #F5F5DC;
    border-radius: 16px;
`;

export default AgentChatForm;