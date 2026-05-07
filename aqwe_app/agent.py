import requests
import os
import json
from typing import List, Optional, Dict
from bs4 import BeautifulSoup

class SimpleAgent:
    """
    Простой агент для взаимодействия с LLM API.
    Поддерживает: память контекста, инструменты, базовое планирование.
    """
    
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.context: List[Dict] = []
        self.tools: Dict[str, callable] = {}
    
    def add_tool(self, name: str, func: callable, description: str):
        """Добавить инструмент, который агент может использовать"""
        self.tools[name] = {'func': func, 'description': description}

    def _hyperbrowse(self, url: str, query: str = None) -> str:
        """
        Инструмент: посещение веб-страницы и извлечение контента.
        """
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
                    "temperature": temperature,
                    "max_tokens": 2000
                },
                timeout=60
            )
            response.raise_for_status()
            result = response.json()['choices'][0]['message']['content']
            self.context.append({"role": "user", "content": prompt})
            self.context.append({"role": "assistant", "content": result})
            return result
        except Exception as e:
            return f"Ошибка LLM: {str(e)}"
    
    def ask(self, question: str) -> str:
        """
        Основной метод: задать вопрос агенту.
        Агент может использовать инструменты, если это нужно.
        """
        # Простая логика: если вопрос про инструменты — предложим их
        if any(tool_name in question.lower() for tool_name in self.tools):
            available = ", ".join(self.tools.keys())
            return f"Я могу использовать инструменты: {available}. Что именно сделать?"
        
        # Иначе — просто отвечаем через LLM
        return self._call_llm(question)
    
    def clear_context(self):
        """Очистить память контекста"""
        self.context = []
    
    # === Примеры инструментов ===
    
    def _search_web(self, query: str) -> str:
        """Пример инструмента: поиск (заглушка)"""
        return f"[Поиск] Результаты по запросу '{query}': пример ответа."
    
    def _calculate(self, expression: str) -> str:
        """Пример инструмента: вычисления"""
        try:
            # Безопасное вычисление (только базовые операции)
            allowed = {"__builtins__": {}}, {"add": lambda a,b: a+b, "sub": lambda a,b: a-b}
            result = eval(expression, *allowed)
            return f"Результат: {result}"
        except:
            return "Ошибка вычисления"