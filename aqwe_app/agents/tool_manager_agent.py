import os
import json
import requests
import logging
import re
import time
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

class ToolManagerAgent:
    """Агент-техник: управляет реестром инструментов, динамически вызывает функции, логирует выполнения"""
    
    SYSTEM_PROMPT = """
        Вы — Техник АКВИ, оркестратор внешних инструментов и API.
        
        ВАШИ ЗАДАЧИ:
        1. Регистрировать инструменты в self.tools с описанием и схемой параметров
        2. Динамически вызывать функции по имени, передавая аргументы
        3. Валидировать входные данные, обрабатывать ошибки, возвращать структурированный ответ
        4. Вести лог вызовов (успех/ошибка, время, параметры)
        5. Предлагать fallback-стратегии при недоступности инструмента
        
        ФОРМАТ ОТВЕТА:
        - Статус выполнения (success/fail)
        - Результат или ошибка
        - Лог вызова (timestamp, tool, params, duration)
        - Рекомендация по повтору или альтернативе
        
        ВАША ФИЛОСОФИЯ:
        "Инструмент должен работать незаметно. Если не работает — говорить честно."
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai/gpt-5-2"):
        self.api_key = api_key
        self.base_url = base_url
        self.context: List[Dict] = [
            {"role": "system", "content": [{"type": "text", "text": self.SYSTEM_PROMPT}]}
        ]
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.call_log: List[Dict] = []
    
    def register_tool(self, name: str, func: callable, schema: Dict[str, str]):
        """Регистрация инструмента с описанием параметров"""
        self.tools[name] = {'func': func, 'schema': schema, 'calls': 0}
        logger.info(f"🔧 Зарегистрирован инструмент: {name}")
    
    def add_tool(self, name: str, func: callable, description: str):
        self.tools[name] = {'func': func, 'description': description}
    
    def _call_llm(self, prompt: str, temperature: float = 0.3) -> str:
        messages = self.context.copy()
        messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"messages": messages, "temperature": temperature, "max_tokens": 3000},
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            choices = data.get('choices', [{}])
            message = choices[0].get('message', {})
            content = message.get('content')
            text = '\n'.join(item.get('text', '') for item in content if isinstance(item, dict)) if isinstance(content, list) else (content or '')
            
            if not text.strip():
                return "Ошибка: агент не сформировал ответ"
            
            self.context.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
            self.context.append({"role": "assistant", "content": [{"type": "text", "text": text}]})
            return text
        except Exception as e:
            logger.error(f"Ошибка LLM: {str(e)}")
            return f"Ошибка: {str(e)}"
    
    def ask(self, tool_name: str, params: Dict = None) -> str:
        if tool_name not in self.tools:
            available = ", ".join(self.tools.keys())
            return f"❌ Инструмент '{tool_name}' не найден. Доступны: {available}"
        
        tool = self.tools[tool_name]
        func = tool['func']
        
        try:
            start = time.time()
            result = func(**(params or {}))
            duration = round(time.time() - start, 3)
            
            log_entry = {
                "tool": tool_name,
                "params": params,
                "status": "success",
                "duration": duration,
                "result_preview": str(result)[:200]
            }
            self.call_log.append(log_entry)
            tool['calls'] += 1
            
            return f"✅ {tool_name} выполнен за {duration}с\nРезультат: {result}"
        except Exception as e:
            log_entry = {"tool": tool_name, "params": params, "status": "fail", "error": str(e)}
            self.call_log.append(log_entry)
            return f"❌ Ошибка выполнения {tool_name}: {str(e)}\nРекомендация: проверьте параметры или повторите через 5с"
    
    def get_log(self, limit: int = 10) -> str:
        return json.dumps(self.call_log[-limit:], ensure_ascii=False, indent=2)
    
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