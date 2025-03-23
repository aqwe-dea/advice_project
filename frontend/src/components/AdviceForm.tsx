import React, { useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';

interface AdviceFormData {
    category: string;
    question: string;
}
function AdviceForm() {
    const [formData, setFormData] = useState<AdviceFormData>({
        category: '',
        question: '',
    });
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const response = await axios.post(
                'http://127.0.0.1:8000/api/advice/',
                formData
            );
            alert('Вопрос успешно отправлен!');
        } catch (error) {
            console.error('Ошибка при отправке вопроса:', error);
            alert('Произошла ошибка при отправке вопроса');
        }
    };

    return (
        <motion.form
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
            <input
             type="text"
             placeholder="Категория..."
             value={formData.category}
             onChange={(e) =>
                setFormData({ ...formData, category: e.target.value })
             }
            />
            <textarea
             placeholder="Задайте вопрос..."
             value={formData.question}
             onChange={(e) =>
                setFormData({ ...formData, question: e.target.value })
             }
            />
            <button type="submit">Отправить</button>
        </motion.form>
    );
}

export default AdviceForm;