import os
import json
import requests
import logging
import re
import time
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup  # ← Добавлен импорт!

logger = logging.getLogger(__name__)

class ToolManagerAgent:
    """Агент-техник: управляет реестром инструментов, динамически вызывает функции"""
    
    SYSTEM_PROMPT = """
        Вы — Техник АКВИ, оркестратор внешних инструментов и API.

        ВАШИ ЗАДАЧИ:
            1. Динамически выбирать и вызывать инструменты по запросу пользователя
            2. Валидировать входные данные, обрабатывать ошибки
            3. Возвращать структурированный ответ: статус, результат, лог
            4. Предлагать fallback при недоступности инструмента

        ФОРМАТ ОТВЕТА:
            - Краткий итог выполнения
            - Результат или ошибка
            - Рекомендации при необходимости
        
        ИНСТРУМЕНТЫ:
            У тебя есть доступ к:
                - googleSearch: для поиска инструмента и других запросов пользователя
                - hyperbrowse: для просмотра актуальной информации с переходом на страницу

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
    
    def add_tool(self, name: str, func: callable, description: str, parameters: Dict = None):
        """Единый метод регистрации инструмента"""
        self.tools[name] = {
            'func': func,
            'description': description,
            'parameters': parameters or {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Запрос"}},
                "required": ["query"]
            }
        }
        logger.info(f"🔧 Зарегистрирован инструмент: {name}")
    
    def _build_api_tools(self) -> List[Dict]:
        """Построить список инструментов в формате API"""
        api_tools = []
        for name, info in self.tools.items():
            api_tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": info['description'],
                    "parameters": info['parameters']
                }
            })
        return api_tools
    
    def _extract_text_or_tool(self, data: dict) -> tuple[str, Optional[Dict]]:
        """Извлечь текст или function_call из ответа API"""
        try:
            choices = data.get('choices', [{}])
            if not choices:
                return "", None
            
            message = choices[0].get('message', {})
            
            # Проверка на function_call
            if 'function_call' in message:
                return "", message['function_call']
            
            # Проверка на tool_calls (OpenAI-стиль)
            if 'tool_calls' in message and message['tool_calls']:
                tool_call = message['tool_calls'][0]['function']
                return "", {
                    'name': tool_call.get('name'),
                    'arguments': tool_call.get('arguments', '{}')
                }
            
            # Обычный текст
            content = message.get('content')
            if isinstance(content, list):
                text = '\n'.join(item.get('text', '') for item in content if isinstance(item, dict))
            else:
                text = content or ''
            
            return text.strip(), None
            
        except Exception as e:
            logger.error(f"Ошибка извлечения: {str(e)}")
            return "", None
    
    def _call_llm(self, prompt: str, max_retries: int = 2) -> str:
        """Вызов LLM с обработкой function_call"""
        
        for attempt in range(max_retries):
            messages = self.context.copy()
            messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
            
            api_tools = self._build_api_tools()
            
            try:
                response = requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "messages": messages,
                        "tools": api_tools if api_tools else None,
                        "tool_choice": "auto",  # ← Разрешить выбор инструмента
                        "temperature": 0.3,
                        "max_tokens": 10000
                    },
                    timeout=120
                )
                response.raise_for_status()
                data = response.json()
                
                text, tool_call = self._extract_text_or_tool(data)
                
                # Если модель запросила инструмент — выполняем его
                if tool_call:
                    func_name = tool_call.get('name')
                    # Парсим аргументы (могут быть JSON-строкой)
                    args_str = tool_call.get('arguments', '{}')
                    if isinstance(args_str, str):
                        try:
                            args = json.loads(args_str)
                        except:
                            args = {'query': args_str}
                    else:
                        args = args_str
                    
                    logger.info(f"🔧 Function call: {func_name}({args})")
                    
                    if func_name in self.tools:
                        func = self.tools[func_name]['func']
                        try:
                            result = func(**args)
                            # Отправляем результат обратно в LLM для финального ответа
                            messages.append({"role": "assistant", "content": [{"type": "text", "text": f"Calling {func_name}..."}]})
                            messages.append({"role": "user", "content": [{"type": "text", "text": f"Result of {func_name}: {result}"}]})
                            
                            # Повторный запрос для получения человеческого ответа
                            second_response = requests.post(
                                f"{self.base_url}/v1/chat/completions",
                                headers={
                                    "Authorization": f"Bearer {self.api_key}",
                                    "Content-Type": "application/json"
                                },
                                json={
                                    "messages": messages,
                                    "temperature": 0.3,
                                    "max_tokens": 10000
                                },
                                timeout=120
                            )
                            second_response.raise_for_status()
                            second_data = second_response.json()
                            final_text, _ = self._extract_text_or_tool(second_data)
                            return final_text or f"✅ {func_name} выполнен. Результат: {result}"
                        except Exception as e:
                            return f"❌ Ошибка выполнения {func_name}: {str(e)}"
                    else:
                        return f"⚠️ Инструмент '{func_name}' не зарегистрирован"
                
                # Обычный текстовый ответ
                if text:
                    self.context.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
                    self.context.append({"role": "assistant", "content": [{"type": "text", "text": text}]})
                    return text
                
                return "Ошибка: не удалось получить ответ от модели"
                
            except requests.Timeout:
                if attempt == max_retries - 1:
                    return "Ошибка: таймаут соединения"
                continue
            except Exception as e:
                logger.error(f"Ошибка LLM (попытка {attempt+1}): {str(e)}")
                if attempt == max_retries - 1:
                    return f"Ошибка: {str(e)}"
                continue
        
        return "Ошибка: исчерпаны попытки выполнения"
    
    def ask(self, question: str) -> str:
        """Основной метод: задать вопрос агенту (LLM выбирает инструмент)"""
        return self._call_llm(question)
    
    def call_tool_direct(self, tool_name: str, params: Dict = None) -> str:
        """Прямой вызов инструмента (для тестов)"""
        if tool_name not in self.tools:
            return f"❌ Инструмент '{tool_name}' не найден. Доступны: {', '.join(self.tools.keys())}"
        
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
            
            return f"✅ {tool_name} выполнен за {duration}с\nРезультат: {result}"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def get_log(self, limit: int = 10) -> str:
        return json.dumps(self.call_log[-limit:], ensure_ascii=False, indent=2)
    
    def _hyperbrowse(self, url: str, query: str = None) -> str:
        try:
            response = requests.get(url)
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
        self.context = [{"role": "system", "content": [{"type": "text", "text": self.SYSTEM_PROMPT}]}]
    
    def _googleSearch(self, query: str) -> str:
        return f"[googleSearch] Результаты по запросу '{query}': пример ответа."
    
    def _calculate(self, expression: str) -> str:
        try:
            allowed = {"__builtins__": {}}, {"add": lambda a,b: a+b, "sub": lambda a,b: a-b}
            result = eval(expression, *allowed)
            return f"Результат: {result}"
        except:
            return "Ошибка вычисления"