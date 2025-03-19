import React, { useState } from 'react';
import axios from 'axios';
import '../styles/AdviceForm.css';
import { motion } from 'framer-motion';

interface AdviceFormData {
    category: string;
    question: string;
}
interface AdviceForm {
    onSuccess?: () => void;
}

function AdviceForm({ onSuccess }: AdviceForm) {
    const [formData, setFormData] = useState<AdviceFormData>({
        category: '',
        question: '',
    });
    const [errors, setErrors] = useState<{ [key: string]: string }>({});

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
           const response = await axios.post('http://127.0.0.1:8000/api/advice/', formData);
            alert('Вопрос успешно отправлен!');
            onSuccess?.();
        } catch (error) {
            console.error('Ошибка при отправке вопроса:', error );
            alert('Произошла ошибка при отправке вопроса');
        }
        const formErrors: { [key: string]: string } = {};
        if (!formData.category.trim()) {
            formErrors.category = 'Пожалуйста, укажите категорию';
        }
        if (!formData.question.trim()) {
            formErrors.question = 'Пожалуйста, задайте вопрос';
        }
        if (Object.keys(formErrors).length > 0) {
            setErrors(formErrors);
            return;
        }

        try {
            const response = await axios.post('http://127.0.0.1:8000/api/advice/', formData);
            console.log(response.data);
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
//return (
//        <form onSubmit={handleSubmit}>
//            <div>
//                <label>Категория:</label>
//                <input
//                type="text"
//                value={formData.category}
//                onChange={(e) =>
//                    setFormData({ ...formData, category: e.target.value })
//                }
//                />
//                {errors.category && <span style={{ color: 'red' }}>{errors.category}</span>}
//            </div>
//            <div>
//                <label>Вопрос:</label>
//                <textarea
//                value={formData.question}
//                    onChange={(e) =>
//                        setFormData({ ...formData, question: e.target.value })
//                    } 
//                    />
//                   {errors.question && <span style={{ color: 'red' }}>{errors.question}</span>}
//            </div>
//            <motion.button
//            whileHover={{ scale: 1.05 }}
//            whileTap={{ scale: 0.95 }}
//            transition={{ type: 'spring', stiffness: 300 }}
//            className="submit-button">Отправить
//            </motion.button>
//        </form>
//    );
//}

