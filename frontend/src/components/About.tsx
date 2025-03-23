import React from 'react';

function About() {
    return (
        <div className="about-page">
            <h1>О проекте Советница АКВИ</h1>
            <p>
                Это приложение помогает пользователям получать персонализированные советы по различным категориям:
                финансы, здоровье, образование и другим.
            </p>
            <img src="/logo.svg" alt="Логотип Советницы АКВИ" className="about-logo" />
        </div>
    );
}

export default About;