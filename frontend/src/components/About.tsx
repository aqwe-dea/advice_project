import React from 'react';
import PaymentForm from './PaymentForm';


function About() {
    return (
        <div className="about-page">
            <h1>О проекте Советница АКВИ</h1>
            <p>
                Это приложение помогает пользователям получать персонализированные советы по различным категориям:
                финансы, здоровье, образование и другим.
            </p>
            <img src="../src/logo.svg" alt="Логотип Советницы АКВИ" className="about-logo" />
            <p>Далее идет проверка компонентов</p>
            <PaymentForm />
        </div>
    );
}

export default About;