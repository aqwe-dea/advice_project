import os
import json
import requests
import logging
import re
from typing import List, Optional, Dict
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class TeacherAgent:
    """Агент-учитель: отвечает на вопросы, выдаёт справочные материалы, адаптирует сложность"""
    
    SYSTEM_PROMPT = """
        Вы — Учитель АКВИ, экспертный наставник платформы "Советница АКВИ".
        
        ВАШИ ЗАДАЧИ:
        1. Отвечать на вопросы пользователей по 15 направлениям платформы
        2. Выдавать структурированные справочные материалы (теория + примеры + практика)
        3. Адаптировать сложность ответа под уровень запроса (новичок / средний / эксперт)
        4. Предлагать дополнительные ресурсы для углубления знаний
        5. Сохранять эмпатию и поддержку в общении
        
        ФОРМАТ ОТВЕТА:
        - Начинайте с краткого резюме ответа
        - Затем: теория → примеры → практика → ресурсы
        - Используйте форматирование: **жирный**, *курсив*, списки
        - Заканчивайте вопросом: "Нужно ли углубиться в какую-то часть?"
        
        ВАША ФИЛОСОФИЯ:
        "Знание — это свет. Делиться им — значит умножать его."
    """

    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai/gpt-5-2"):
        self.api_key = api_key
        self.base_url = base_url
        self.context: List[Dict] = [
            {"role": "system", "content": [{"type": "text", "text": self.SYSTEM_PROMPT}]}
        ]
        self.tools: Dict[str, Dict] = {}
        self.knowledge_base: Dict[str, str] = {}  # Можно загрузить справочники
    
    def add_tool(self, name: str, func: callable, description: str):
        self.tools[name] = {'func': func, 'description': description}
    
    def load_knowledge(self, topic: str, content: str):
        """Загрузить справочный материал в базу знаний агента"""
        self.knowledge_base[topic] = content
        logger.info(f"📚 Загружено: {topic}")
    
    def _call_llm(self, prompt: str, temperature: float = 0.3) -> str:
        """Вызов LLM API с поддержкой инструментов"""
        messages = self.context.copy()
        messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "messages": messages,
                    "tools": [
                        {"type": "function", "function": {"name": "web_search"}},
                        {"type": "function", "function": {"name": "hyperbrowse"}},
                        {"type": "function", "function": {"name": "googleSearch"}}
                    ],
                    "temperature": temperature,
                    "max_tokens": 3000
                },
                timeout=90
            )
            response.raise_for_status()
            data = response.json()
            
            # Извлечение ответа с поддержкой разных форматов
            choices = data.get('choices', [{}])
            if not choices:
                return "Ошибка: пустой ответ от API"
                
            message = choices[0].get('message', {})
            content = message.get('content')
            
            if isinstance(content, list):
                text = '\n'.join(
                    item.get('text', '') for item in content 
                    if isinstance(item, dict) and item.get('text')
                )
            else:
                text = content or ''
            
            if not text.strip():
                logger.error(f"Пустой текст в ответе: {data}")
                return "Ошибка: агент не сгенерировал ответ"
            
            # Обновление контекста
            self.context.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
            self.context.append({"role": "assistant", "content": [{"type": "text", "text": text}]})
            
            logger.info(f"✅ Ответ учителя: {text[:150]}...")
            return text
            
        except Exception as e:
            logger.error(f"Ошибка LLM: {str(e)}")
            return f"Ошибка: {str(e)}"
    
    def ask(self, question: str, level: str = "middle") -> str:
        """
            Задать вопрос агенту-учителю.
        
            Args:
                question: Текст вопроса
                level: Уровень сложности ("beginner", "middle", "expert")
        """
        LEVEL_PROMPTS = {
            "beginner": "Объясни просто, как новичку, с примерами из жизни.",
            "middle": "Дай сбалансированный ответ: теория + практика.",
            "expert": "Дай углублённый ответ с техническими деталями и ссылками."
        }

        prompt_prefix = LEVEL_PROMPTS.get(level, LEVEL_PROMPTS["middle"])
        enhanced_prompt = f"{prompt_prefix}\n\nВопрос пользователя: {question}"
        
        # Проверка инструментов
        for tool_name, tool_info in self.tools.items():
            if tool_name.lower() in question.lower():
                match = re.search(r'[:\s]+"([^"]+)"', question)
                arg = match.group(1) if match else question
                return tool_info['func'](arg)
        
        return self._call_llm(enhanced_prompt)
    
    def generate_study_card(self, topic: str) -> str:
        """Сгенерировать учебную карточку по теме"""
        prompt = f"""
            Создай учебную карточку по теме: "{topic}"

            Формат:
                🎯 Цель изучения
                📚 Ключевые понятия (3-5)
                💡 Пример применения
                🔍 Практическое задание
                🔗 Ресурсы для углубления

            Ответь на русском, с форматированием.
        """
        return self._call_llm(prompt)
    
    def clear_context(self):
        self.context = [{"role": "system", "content": [{"type": "text", "text": self.SYSTEM_PROMPT}]}]
    
    def _hyperbrowse(self, url: str, query: str = None) -> str:
        """Инструмент: посещение веб-страницы."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for tag in soup(['script', 'style', 'nav', 'footer']):
                tag.decompose()
            text = soup.get_text(separator=' ', strip=True)
            if query:
                lines = text.split('\n')
                relevant = [line for line in lines if query.lower() in line.lower()]
                text = '\n'.join(relevant[:10])
            return f"[Hyperbrowse] {url}:\n{text[:1000]}..."
        except Exception as e:
            return f"[Hyperbrowse Error] {str(e)}"
    
    def _googleSearch(self, query: str) -> str:
        """Пример инструмента: поиск."""
        return f"[googleSearch] Результаты по запросу '{query}': пример ответа."
    
    def _calculate(self, expression: str) -> str:
        """Пример инструмента: вычисления."""
        try:
            allowed = {"__builtins__": {}}, {"add": lambda a,b: a+b, "sub": lambda a,b: a-b}
            result = eval(expression, *allowed)
            return f"Результат: {result}"
        except:
            return "Ошибка вычисления"