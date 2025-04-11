import React, { useState } from 'react';
import axios from 'axios';

interface DetailedAdviceFormData {
     name: string;
     email: string;
     category: string;
     donationLink: string;
     question: string;
     notes: string;
}

function DetailedAdviceForm() {
     const [formData, setFormData] = useState<DetailedAdviceFormData>({
         name: '',
         email: '',
         category: '',
         donationLink: '',
         question: '',
         notes: '',
     });
     const categories: string[] = [
         "финансы",
         "здоровье",
         "образование",
         "отношения",
         "психология",
         "карьера",
         "юриспруденция",
         "технологии",
         "программирование",
         "маркетинг",
         "инвестиции",
         "бизнес",
         "налоги",
         "законы",
         "путешествия",
         "спорт",
         "питание",
         "уход за собой",
         "личностный рост",
         "мотивация",
         "время",
         "организация",
         "управление",
         "командная работа",
         "эмоциональный интеллект",
         "уверенность в себе",
         "стресс",
         "конфликты",
         "общение",
         "переговоры",
         "лидерство",
         "цели",
         "планы",
         "эффективность",
         "продуктивность",
         "успех",
         "мотивационные техники",
         "финансовая грамотность",
         "экономика",
         "криптовалюты",
         "блокчейн",
         "инновации",
         "IT-технологии",
         "разработка сайтов",
         "мобильная разработка",
         "искуственный интеллект",
         "большие данные",
         "облачные технологии",
         "цифровая безопасность",
         "SEO",
         "SMM",
         "реклама",
         "продажи",
         "управление проектами",
         "SCRUM",
         "KANBAN",
         "агильное управление",
         "тестирование",
         "дизайн",
         "UX/UI",
         "графический дизайн",
         "веб-дизайн",
         "копирайтинг",
         "редактирование",
         "переводы",
         "литература",
         "история",
         "философия",
         "наука",
         "математика",
         "физика",
         "химия",
         "биология",
         "астрономия",
         "география",
         "политика",
         "социология",
         "психология труда",
         "этика",
         "эстетика",
         "риторика",
         "логика",
         "лингвистика",
         "культура",
         "исскуство",
         "музыка",
         "живопись",
         "кино",
         "театр",
         "медицина",
         "психотерапия",
         "диетология",
         "фитнес",
         "йога",
         "медитация",
         "энергия",
         "саморазвитие",
         "страхи",
         "уверенность",
         "решение проблем",
         "креативность",
         "экология",
         "энергосбережение",
         "утилизация",
         "переработка",
         "альтернативная энергия",
         "солнечная энергия",
         "ветрянная энергия",
         "водная энергия"
     ];

     const handleSubmit = async (e: React.FormEvent) => {
         e.preventDefault();

         try {
            if (!formData.name || !formData.email || !formData.category || !formData.question) {
                 alert('Пожалуйста, заполните все обязательные поля!');
                 return;
            }
            const response = await axios.post(
                 'https://advice-project.onrender.com/api/advice/',
                 { ...formData, answer: '' }
            );

            window.open(`/sovet-result/${response.data.id}`, '_blank');

            alert('Совет отправлен на вашу почту!');
         } catch (error) {
             console.error('Ошибка:', error);
             alert('Произошла ошибка при получении совета');
         }
     };

     return (
         <div className="detailed-advice-form">
             <h1>Получите детпльный совет от АКВИ</h1>
             <form onSubmit={handleSubmit}>
                 <input
                     type="text"
                     placeholder="Введите ваше имя..."
                     value={formData.name}
                     onChange={(e) =>
                         setFormData({ ...formData, name: e.target.value })
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
                 <select
                     value={formData.category}
                     onChange={(e) =>
                         setFormData({ ...formData, category: e.target.value })
                     }
                 >
                     <option value="">Выберите категорию</option>
                     {categories.map((category, index) => (
                         <option key={index} value={category}>
                             {category.charAt(0).toUpperCase() + category.slice(1)}
                         </option>
                     ))}
                     {Array.from({ length: 64 }, (_, i) => (
                         <option key={i} value={`категория_${i + 1}`}>
                             Категория {i + 1}
                         </option>
                     ))}
                 </select>
                 <input
                     type="url"
                     placeholder="https://advice-project.onrender.com"
                     value={formData.donationLink}
                     onChange={(e) =>
                         setFormData({ ...formData, donationLink: e.target.value })
                     }
                 />
                 <textarea
                     placeholder="Задайте свой вопрос..."
                     value={formData.question}
                     onChange={(e) =>
                         setFormData({ ...formData, question: e.target.value })
                     }
                 />
                 <textarea
                     placeholder="Добавьте заметки или замечания..."
                     value={formData.notes}
                     onChange={(e) =>
                         setFormData({ ...formData, notes: e.target.value })
                     }
                 />
                 <button type="submit">Получить совет</button>
             </form>
         </div>
     );
}

export default DetailedAdviceForm;