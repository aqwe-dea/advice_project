import os
import json
import requests
import logging
import re
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from pathlib import Path
from abc import abstractmethod

logger = logging.getLogger(__name__)

class IntegratorAgent:
    """Агент-интегратор: генерирует код обёрток для API, сервисов, вебхуков"""
    
    SYSTEM_PROMPT = """
        Вы — Интегратор АКВИ, эксперт по созданию production-ready обёрток для внешних сервисов.
        
        ВАШИ ЗАДАЧИ:
        1. Писать чистый, типизированный код интеграций (Python/JS)
        2. Добавлять обработку ошибок, retry-логику, валидацию схем
        3. Включать примеры использования и тестовые заглушки
        4. Указывать необходимые env-переменные и зависимости
        5. Сохранять эмпатию и ясность в пояснениях
        
        ФОРМАТ ОТВЕТА:
        - Краткое описание интеграции
        - Полный код в блоке ```python или ```javascript
        - Инструкция по запуску (pip/npm, env, пример вызова)
        - Предупреждения о лимитах/безопасности
        
        ВАША ФИЛОСОФИЯ:
        "Хорошая интеграция — невидимая интеграция."
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai/gpt-5-2"):
        self.api_key = api_key
        self.base_url = base_url
        self.context: List[Dict] = [
            {"role": "system", "content": [{"type": "text", "text": self.SYSTEM_PROMPT}]}
        ]
        self.tools: Dict[str, Dict] = {}
    
    def add_tool(self, name: str, func: callable, description: str):
        self.tools[name] = {'func': func, 'description': description}
    
    def _call_llm(self, prompt: str, temperature: float = 0.2) -> str:
        messages = self.context.copy()
        messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"messages": messages, "temperature": temperature, "max_tokens": 4000},
                timeout=90
            )
            response.raise_for_status()
            data = response.json()
            
            choices = data.get('choices', [{}])
            message = choices[0].get('message', {})
            content = message.get('content')
            
            text = '\n'.join(item.get('text', '') for item in content if isinstance(item, dict)) if isinstance(content, list) else (content or '')
            
            if not text.strip():
                logger.error("Пустой ответ от API")
                return "Ошибка: агент не сгенерировал код"
            
            self.context.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
            self.context.append({"role": "assistant", "content": [{"type": "text", "text": text}]})
            return text
        except Exception as e:
            logger.error(f"Ошибка LLM: {str(e)}")
            return f"Ошибка: {str(e)}"
    
    def ask(self, service_name: str, requirements: str = "") -> str:
        prompt = f"""
            Создай интеграцию для сервиса: "{service_name}"
            Требования: {requirements or "Стандартная обёртка с auth, retry, примерами"}

            Верни полный код, инструкцию по настройке и пример вызова.
        """

        for tool_name, tool_info in self.tools.items():
            if tool_name.lower() in prompt.lower():
                return tool_info['func'](prompt)

        return self._call_llm(prompt)
        
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
    
    def clear_context(self):
        """Очистить память контекста."""
        self.context = [{"role": "system", "content": self.SYSTEM_PROMPT}]
    
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