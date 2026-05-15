import os
import json
import requests
import logging
from .short_term import ShortTermMemory
from .long_term import LongTermMemory
from .learner import ExperienceLearner
from typing import List, Optional, Dict
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class SmartAgent:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.learner = ExperienceLearner(self.long_term)
        self.context: List[Dict] = []
        self.tools: Dict[str, callable] = {}
    
    def add_tool(self, name: str, func: callable, description: str):
        self.tools[name] = {"func": func, "description": description}
    
    def _call_llm(self, prompt: str, temperature: float = 0.7) -> str:
        """Внутренний вызов к LLM API"""
        messages = self.context.copy()
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "stream": False,
                    "messages": messages,
                    "temperature": temperature
                }
            )
            logger.info(f"Полный ответ API: {response.json()}")
            response.raise_for_status()
            #result = response.json()['choices'][0]['message']['content']
            data = response.json()
            #result = data.get('resultText')
            #result = data.get('data', {}).get('resultJson', {})
            result = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            self.context.append({"role": "user", "content": prompt})
            self.context.append({"role": "assistant", "content": result})
            return result
        except Exception as e:
            return f"Ошибка LLM: {str(e)}"

    def ask(self, question: str, user_feedback: str = None) -> str:
        # 1. Ищем похожий прошлый опыт
        similar = self.long_term.find_similar(question)
        
        # 2. Формируем промпт с учётом опыта
        context = ""
        if similar:
            context = f"Похожий прошлый опыт:\n" + "\n".join(similar) + "\n\n"
        
        # 3. Добавляем краткосрочный контекст
        context += "Текущий диалог:\n" + "\n".join(
            f"{m['role']}: {m['content']}" for m in self.short_term.messages[-10:]
        )
        
        # 4. Вызываем LLM с обогащённым контекстом
        answer = self._call_llm(f"{context}\n\nВопрос: {question}")
        
        # 5. Запоминаем в краткосрочную память
        self.short_term.add("user", question)
        self.short_term.add("assistant", answer)
        
        # 6. Если есть фидбек — учимся
        if user_feedback:
            self.learner.evaluate_action(question, answer, answer, user_feedback)

        if any(tool_name in question.lower() for tool_name in self.tools):
            available = ", ".join(self.tools.keys())
            return f"Я могу использовать инструменты: {available}. Что именно сделать?"

        return answer

    def _hyperbrowse(self, url: str, query: str = None) -> str:
        """Инструмент: посещение веб-страницы и извлечение контента."""
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
    
    def _search_web(self, query: str) -> str:
        """Пример инструмента: поиск (заглушка)"""
        return f"[Поиск] Результаты по запросу '{query}': пример ответа."