import React, { useState } from 'react';
import axios from 'axios';


interface SovetFormData {
     category: string;
     question: string;
     email: string;
}

function Sovet() {
     const [formData, setFormData] = useState<SovetFormData>({
         category: '',
         question: '',
         email: '',
     });
    
     const [donationAmount] = useState<number>(5);

     const handleSubmit = async (e: React.FormEvent) => {
         e.preventDefault();
         try {
             await axios.post(
                 'https://advice-project.onrender.com/create-payment-intent/',
                 { amount: donationAmount * 100, currency: 'usd' }
             );
             await axios.post(
                 'https://advice-project.onrender.com/api/advice/',
                 { ...formData, answer: '' }
             );

             alert('Вы получили совет!');
         } catch (error) {
             console.error('Ошибка', error);
             alert('Произошла ошибка при получении совета');
         }
     };

     return (
        <div className="sovet-page">
            <h1>Получите совет от АКВИ</h1>
            <p>Выберите категорию и сделайте пожертвование, чтобы получить совет.</p>
            <select
             value={formData.category}
             onChange={(e) => 
                 setFormData({ ...formData, category: e.target.value })
             }
             >
                <option value="">Выберите категорию</option>
                <option value="финансы">Финансы (5$)</option>
                <option value="здоровье">Здоровье (7$)</option>
                <option value="образование">Образование (10$)</option>
                <option value="реклама">Реклама (12$)</option>
             </select>

             <p>Сумма пожертвования: ${donationAmount}</p>

             <form onSubmit={handleSubmit}>
                 <textarea
                  placeholder="Задайте свой вопрос..."
                  value={formData.question}
                  onChange={(e) =>
                     setFormData({ ...formData, question: e.target.value })
                  }
                  />
                 <input
                   type="email"
                   placeholder="Введите ваш email..."
                   value={formData.email}
                   onChange={(e) =>
                     setFormData({ ...formData, email: e.target.value })
                   }
                   />
                 <button type="submit">Получить Совет</button>
             </form>
         </div>
     );
}

export default Sovet;