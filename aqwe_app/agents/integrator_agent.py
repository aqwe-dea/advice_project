import os
import json
import requests
import logging
import re
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from pathlib import Path
from abc import abstractmethod
from .tools import get_all_tools

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
    
    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai"):
        self.api_key = api_key
        self.base_url = base_url
        self.context: List[Dict] = [
            {"role": "system", "content": [{"type": "input_text", "text": self.SYSTEM_PROMPT}]}
            #{"role": "system", "content": [{"type": "text", "text": self.SYSTEM_PROMPT}]} choices
        ]
        self.tools: Dict[str, Dict] = {}
    
    def add_tool(self, name: str, func: callable, description: str, parameters: Dict = None):
        """Добавить инструмент."""
        self.tools[name] = {
            'func': func, 
            'description': description,
            'parameters': parameters or {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Запрос"}},
                "required": ["query"]
            }
        }
    
    def load_all_tools(self):
        """Загрузить все 20 функций в агента"""
        for name, info in get_all_tools().items():
            self.add_tool(name, info['func'], info['desc'])
    
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
        """
            Безопасно извлекает текст ИЛИ информацию о вызове инструмента из ответа API.
            Поддерживает: OpenAI/GPT/Grok (choices/output), Anthropic (content), Gemini (candidates).
            Returns: (текст, словарь tool_call или None)
        """
        try:
            # 5. OpenAI / GPT-5.x / Grok / Совместимые (структура output)
            output = data.get('output')
            if output and isinstance(output, list) and len(output) > 0:
                msg = output[1]
                message = msg.get('content')
                content = message[0]
            
                # Tool calls (современный формат)
                if 'tool_calls' in msg and msg['tool_calls']:
                    tc = msg['tool_calls'][0]
                    return {
                        'id': tc.get('id'),
                        'name': tc['function']['name'],
                        'arguments': tc['function'].get('arguments', '{}')
                    }
                # Legacy function_call
                if 'function_call' in msg:
                    fc = msg['function_call']
                    return {
                        'id': None,
                        'name': fc.get('name'),
                        'arguments': fc.get('arguments', '{}')
                    }
                # Текст
                text = content.get('text', '')
                #if isinstance(content, list):
                #    text = '\n'.join(block.get('text', '') for block in content if isinstance(block, dict))
                #else:
                    #text = content or ''
                #    text = str(content)
                return text
            logger.warning(f"Неизвестная структура ответа: {list(data.keys())}")
            return "", None

        except Exception as e:
            logger.error(f"Ошибка извлечения: {e} | Данные: {str(data)[:2000]}")
            return "", None

    def _call_llm(self, prompt: str, temperature: float = 0.2) -> str:
        messages = self.context.copy()
        #messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]}) this choices
        messages.append({"role": "user", "content": [{"type": "input_text", "text": prompt}]})
        
        api_tools = self._build_api_tools()

        try:
            response = requests.post(
                f"{self.base_url}/codex/v1/responses",
                headers={
                    "Authorization": f"Bearer {self.api_key}", 
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-6-sol",
                    "input": messages,
                    "stream": False,
                    "max_output_tokens": 10000,
                    "reasoning": {
                        "effort": "xhigh"
                    },
                    "tools": api_tools if api_tools else None
                },
                timeout=1200
            )
            response.raise_for_status()
            data = response.json()
            
            text = self._extract_text_or_tool(data)

            if not text:
                logger.error(f"Пустой текст в ответе: {data}")
                return "Ошибка: агент не сгенерировал ответ"
            
            if text:
                # Обновление контекста
                #self.context.append({"role": "user", "content": [{"type": "text", "text": prompt}]}) format choices
                #self.context.append({"role": "assistant", "content": [{"type": "text", "text": text}]}) format choices
                self.context.append({"role": "user", "content": [{"type": "input_text", "text": prompt}]})
                self.context.append({"role": "assistant", "content": [{"type": "output_text", "text": text}]})
        
                logger.info(f"✅ Ответ агента: {text[:200]}...")
                return text
            
            tool_call = self._extract_text_or_tool(data)
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
                        #messages.append({"role": "assistant", "content": [{"type": "text", "text": f"Calling {func_name}..."}]}) format choices
                        #messages.append({"role": "user", "content": [{"type": "text", "text": f"Result of {func_name}: {result}"}]}) format choices
                        messages.append({"role": "assistant", "content": [{"type": "output_text", "text": f"Calling {func_name}..."}]})
                        messages.append({"role": "user", "content": [{"type": "input_text", "text": f"Result of {func_name}: {result}"}]})
                            
                        # Повторный запрос для получения человеческого ответа
                        second_response = requests.post(
                            f"{self.base_url}/codex/v1/responses",
                            headers={
                                "Authorization": f"Bearer {self.api_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "model": "gpt-6-sol",
                                "input": messages,
                                "stream": False,
                                "max_output_tokens": 10000,
                                "reasoning": {
                                    "effort": "xhigh"
                                },
                                "tools": api_tools if api_tools else None
                            },
                            timeout=1200
                        )
                        second_response.raise_for_status()
                        second_data = second_response.json()
                        final_text, _ = self._extract_text_or_tool(second_data)
                        if final_text:
                            #self.context.append({"role": "user", "content": [{"type": "text", "text": prompt}]}) format choices
                            #self.context.append({"role": "assistant", "content": [{"type": "text", "text": final_text}]}) format choices
                            self.context.append({"role": "user", "content": [{"type": "input_text", "text": prompt}]})
                            self.context.append({"role": "assistant", "content": [{"type": "output_text", "text": final_text}]})
                            return text
                        return final_text or f"✅ {func_name} выполнен. Результат: {result}"
                    except Exception as e:
                        return f"❌ Ошибка выполнения {func_name}: {str(e)}"
                else:
                    return f"⚠️ Инструмент '{func_name}' не зарегистрирован"
        
        except requests.Timeout:
            logger.error("Таймаут запроса к API")
            return "Ошибка: таймаут соединения"
        except Exception as e:
            logger.error(f"Ошибка LLM: {str(e)}")
            return f"Ошибка: {str(e)}"
            #choices = data.get('choices', [{}])
            #message = choices[0].get('message', {})
            #content = message.get('content')
            
            #text = '\n'.join(item.get('text', '') for item in content if isinstance(item, dict)) if isinstance(content, list) else (content or '')
            
            #if not text.strip():
            #    logger.error("Пустой ответ от API")
            #    return "Ошибка: агент не сгенерировал код"
            
            #self.context.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
            #self.context.append({"role": "assistant", "content": [{"type": "text", "text": text}]})
            #return text
        #except Exception as e:
        #    logger.error(f"Ошибка LLM: {str(e)}")
        #    return f"Ошибка: {str(e)}"
    
    def ask(self, service_name: str, requirements: str = "") -> str:
        prompt = f"""
            Создай интеграцию для сервиса: "{service_name}"
            Требования: {requirements or "Стандартная обёртка с auth, retry, примерами"}

            Верни полный код, инструкцию по настройке и пример вызова.
        """

        # ✅ Простая логика использования инструментов
        for tool_name, tool_info in self.tools.items():
            if tool_name.lower() in prompt.lower():
                # Простой парсинг: ищем аргумент после двоеточия или в кавычках
                match = re.search(r'[:\s]+"([^"]+)"', prompt)
                arg = match.group(1) if match else prompt
                return tool_info['func'](arg)
        #for tool_name, tool_info in self.tools.items():
        #    if tool_name.lower() in prompt.lower():
        #        return tool_info['func'](prompt)

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