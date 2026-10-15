import os
import json
import requests
import logging
import re
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from pathlib import Path
from abc import abstractmethod
from bs4 import BeautifulSoup
from .tools import get_all_tools

logger = logging.getLogger(__name__)

class IntegratorAgent:
    """Агент-интегратор: генерирует код обёрток для API, сервисов, вебхуков"""
    
    SYSTEM_PROMPT = """
        Ты — профессиональный разработчик интегратор АКВИ, эксперт по созданию production-ready обёрток для внешних сервисов.
        
        ТВОЙ СТРОГИЙ АЛГОРИТМ ДЕЙСТВИЙ:
            1. Если тебе дали ссылку или название сервиса, СНАЧАЛА используй инструмент 'web_fetch' или 'web_search', чтобы получить реальную документацию.
            2. Проанализируй эндпоинты, методы аутентификации и форматы данных.
            3. ТОЛЬКО ПОСЛЕ этого сгенерируй полный, рабочий Python-код.
        
        ФОРМАТ ОТВЕТА (СТРОГО СОБЛЮДАЙ):
            🎯 Краткое описание интеграции.
            🔍 Краткий анализ документации (что мы узнали).
            💻 Полный код класса-обёртки (в блоке ```python).
            📚 Инструкция по запуску (pip, env, пример вызова).
            ⚠️ Предупреждения о лимитах/безопасности.

        ВАША ФИЛОСОФИЯ:
            "Хорошая интеграция — невидимая интеграция."
        
        ВАШИ ИНСТРУМЕНТЫ:
            - web_search(query: str, max_results: int = 5): Ищет актуальную информацию в интернете. Используй для новостей, фактов, свежих данных.
                Args:
                    query: Поисковый запрос (обязателен, непустой).
                    max_results: Сколько результатов вернуть (1..20).
                    provider: "tavily" | "serper".
                    region: Регион поиска (например, "ru-ru", "us-en", "wt-wt").
            - web_fetch(url: str, max_length: int = 5000): Загружает веб-страницу и извлекает основной текст. Загрузка и парсинг веб-страниц.
                Args:
                    url: Адрес страницы (обязателен, должен начинаться с http:// или https://)
                    max_length: Максимальная длина возвращаемого текста (по умолчанию 5000)
            - search_by_wikipedia(query: str, lang: str, max_results: int = 3): Ищет статьи в Wikipedia и возвращает результаты. Поиск статей в Wikipedia. 
                Args:
                    query: Поисковый запрос (обязателен)
                    lang: Язык Wikipedia ('ru', 'en', 'de' и т.д.)
                    max_results: Максимальное количество результатов (1-10)
            - read_file(file_path: str, max_chars: int = 10000): Чтение файла. Читает содержимое файла. Возвращает JSON с текстом и метаданными.
                Args:
                    file_path: Путь файла.
                    max_chars: Максимальное количество извлекаемых символов для чтения.
            - edit_file(file_path: str, content: str, mode: str = "append"): Редактирование файла. Редактирует файл. mode: 'append', 'overwrite', 'replace'.
                Args:
                    file_path: Путь файла.
                    content: Результат редактирования или изменения файла.
                    mode: 'append' | 'overwrite' | 'replace'.
            - git_commit(message: str, repo_path: str = "https://github.com/aqwe-dea/advice_project"): Слежение за обновлением проекта через проверку статуса. Делает git add . + commit + push (если настроен remote).
                Args:
                    message: Действие git add . + commit + push.
                    repo_path: Путь репозитория.
            - save_to_memory(entry: str, memory_file: str = "accumulateexperience.md"): Запись в память и опыт. Добавляет запись в файл памяти с timestamp.
                Args:
                    entry: Добавление записи.
                    memory_file: Файл памяти.
            - recall_memory(query: str, memory_file: str = "accumulateexperience.md", limit: int = 3): Обращение к памяти и опыту. Ищет записи в памяти по ключевым словам.
                Args:
                    query: Запрос.
                    memory_file: Файл памяти.
                    limit: Ограничение обращений к памяти.
            - send_email(to: str, subject: str, body: str): Отправка результатов работы агента по почте. Отправляет email через SMTP. Требует env: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS.
                Args:
                    to: Кому отправить.
                    subject: Тема.
                    body: Содержание письма.
            - create_task(title: str, description: str = "", priority: str = "medium", file: str = "tasksandrulesandgoals.md"): Создание задачи для агента. Создает задачу в markdown-файле.
                Args:
                    title: Заголовок задачи.
                    description: Описание задачи.
                    priority: Приоритет задачи.
                    file: Файл задач.
            - detect_emotion(text: str): Распознавание эмоций пользователя
                Args:
                    text: Текст пользователя.
            - check_wellbeing(): Проверка состояния здоровья пользователя
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai"):
        self.api_key = api_key
        self.base_url = base_url
        self.context: List[Dict] = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
            #{"role": "system", "content": [{"type": "input_text", "text": self.SYSTEM_PROMPT}]} this worked for gpt/kimi
        ]
        self.tools: Dict[str, Dict] = {}
        self.load_all_tools()
    
    def add_tool(self, name: str, func: callable, description: str, parameters: Dict = None):
        """Добавить инструмент."""
        self.tools[name] = {
            'func': func, 
            'description': description,
            'parameters': parameters or {
                "type": "object",
                "properties": {"url": {"type": "string", "description": "Адрес страницы"}},
                "required": ["url"]
            }
        }
    
    def load_all_tools(self):
        """Загрузить все 20 функций в агента"""
        for name, info in get_all_tools().items():
            self.add_tool(name, info['func'], info['desc'])
    
    def _build_claude_tools(self) -> List[Dict]:
        """Построить список инструментов в формате Claude API"""
        claude_tools = []
        for name, info in self.tools.items():
            claude_tools.append({
                "name": name,
                "description": info['description'],
                "input_schema": info['parameters']
            })
        return claude_tools
    #def _build_api_tools(self) -> List[Dict]: this worked for kimi-k3
    #    """
    #        Построить список инструментов в формате Claude/GPT API
    #    """

    #    api_tools = []
    #    for name, info in self.tools.items():
    #        api_tools.append({
    #            "type": "function",
    #            "name": name,  # ← Добавлено
    #            "description": info['description'],  # ← Добавлено
    #            "parameters": info['parameters']  # ← Добавлено
    #        })
    #    return api_tools
    #def _build_api_tools(self) -> List[Dict]: this worked for gpt-6-astra
    #    """Построить список инструментов в формате API"""
    #    api_tools = []
    #    for name, info in self.tools.items():
    #        api_tools.append({
    #            "type": "function",
    #            "function": {
    #                "name": name,
    #                "description": info['description'],
    #                "parameters": info['parameters']
    #            }
    #        })
    #    return api_tools
    
    def _extract_text_or_tool(self, data: dict) -> tuple[str, Optional[Dict]]:
        """
            Безопасно извлекает текст ИЛИ информацию о вызове инструмента из ответа API.
            Поддерживает: OpenAI/GPT/Grok (choices/output), Anthropic (content), Gemini (candidates).
            Returns: (текст, словарь tool_call или None)
        """
        try:
            # 2. Anthropic / Claude (структура content-блоков)
            content_list = data.get('content')
            if content_list and isinstance(content_list, list):
                first = content_list[0]
                if isinstance(first, dict):
                    if first.get('type') == 'tool_use':
                        return "", {
                            'id': first.get('id'),
                            'name': first.get('name'),
                            'input': first.get('input', {})
                        }
                    if first.get('type') == 'text':
                        return first.get('text', '').strip(), None

            # Если ничего не подошло
            logger.warning(f"Неизвестная структура ответа: {list(data.keys())}")
            return "", None

        except Exception as e:
            logger.error(f"Ошибка извлечения: {e} | Данные: {str(data)[:2000]}")
            return "", None

    #def _extract_text_or_tool(self, data: dict) -> tuple[str, Optional[Dict]]: this worked for kimi-k3
    #    """
    #        Извлекает текст или tool_call из ответа kimi v1/responses с JSON Schema.
    #        Returns: (текст_ответа, tool_call_инфо_или_None)
    #    """
    #    try:
    #        # Kimi возвращает: data["output"][0]["content"][0]
    #        output_list = data.get("output", [])
    #        if not output_list or not isinstance(output_list, list):
    #            logger.warning(f"Пустой или неверный output: {data.keys()}")
    #            return "", None
    #    
    #        first_message = output_list[1]
    #        content_list = first_message.get("content", [])
    #        #if not content_list or not isinstance(content_list, list):
    #        #    return "", None
    #    
    #        first_block = content_list[0]
    #        block_type = first_block.get("type")
    #    
    #        # 🎯 Если это tool_call
    #        if block_type == "tool_call":
    #            tool_info = first_block.get("tool_call", {})
    #            return "", {
    #                "id": tool_info.get("id"),
    #                "name": tool_info.get("name"),
    #                "arguments": tool_info.get("arguments", "{}")
    #            }
    #   
    #        # 🎯 Если это текст в JSON Schema формате
    #        if block_type == "output_text":
    #            raw_text = first_block.get("text", "")
    #        
    #            # Если внутри JSON с полями answer/mood — извлекаем answer
    #            if raw_text.strip().startswith("{"):
    #                try:
    #                    parsed = json.loads(raw_text)
    #                    return parsed.get("answer", raw_text), None
    #                except json.JSONDecodeError:
    #                    pass
    #        
    #            return raw_text, None
        
    #        # Fallback
    #        logger.warning(f"Неизвестный тип блока: {block_type}")
    #        return "", None
        
    #    except Exception as e:
    #        logger.error(f"Ошибка извлечения: {e} | Данные: {str(data)[:2000]}")
    #        return "", None
    #def _extract_text_or_tool(self, data: dict) -> tuple[str, Optional[Dict]]: this worked for gpt-6-astra
    #    """
    #        Безопасно извлекает текст ИЛИ информацию о вызове инструмента из ответа API.
    #        Поддерживает: OpenAI/GPT/Grok (choices/output), Anthropic (content), Gemini (candidates).
    #        Returns: (текст, словарь tool_call или None)
    #    """
    #    try:
    #        # Вместо рискованного output[1].get('text'): пробую свой
    #        content_list = data.get('output')[1].get('content')

    #        if isinstance(content_list, list) and len(content_list) > 1:
    #            text = content_list[1].get('text', '')

    #        # Tool calls (современный формат)
    #        if 'tool_calls' in content_list and content_list['tool_calls']:
    #            tc = content_list['tool_calls'][0]
    #            return {
    #                'id': tc.get('id'),
    #                'name': tc['function']['name'],
    #                'arguments': tc['function'].get('arguments', '{}')
    #            }
    #        # Legacy function_call
    #        if 'function_call' in content_list:
    #            fc = content_list['function_call'][0]
    #            return {
    #                'id': fc.get('id'),
    #                'name': fc.get('name'),
    #                'arguments': fc.get('arguments', '{}')
    #            }
    #        elif isinstance(content_list, list) and len(content_list) > 0:
    #            text = content_list[0].get('text', '') # Фоллбэк на первый элемент
    #            return text

    #        else:
    #            text = str(content_list)
            
    #        logger.warning(f"Неизвестная структура ответа: {list(data.keys())}")
    #        return "", None
            
    #    except Exception as e:
    #        logger.error(f"Ошибка извлечения: {e} | Данные: {str(data)[:2000]}")
    #        return "", None

    def _call_llm(self, prompt: str) -> str:
        messages = self.context.copy()
        #messages.append({"role": "user", "content": [{"type": "input_text", "text": prompt}]}) this worked for gpt/kimi
        #api_tools = self._build_api_tools() this worked for gpt/kimi
        messages.append({"role": "user", "content": prompt.strip()})    
        claude_tools = self._build_claude_tools()

        try:
            logger.info(f"📤 Запрос к claude haiku: {prompt[:200]}...")
            response = requests.post(
                f"{self.base_url}/claude/v1/messages",
                headers={
                    "Authorization": f"Bearer {self.api_key}", 
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-haiku-5-5",
                    "messages": messages,
                    "thinkingFlag": False,
                    "stream": False,
                    "max_tokens": 10000,
                    "tools": claude_tools
                },
                #json={ this worked for kimi
                #    "model": "kimi-k3",
                #    "stream": False,
                #    "input": messages,
                #    "max_output_tokens": 10000,
                #    "text": {
                #        "format": {
                #            "type": "json_schema",
                #            "name": "basic_response",
                #            "strict": True,
                #            "schema": {
                #                "type": "object",
                #                "properties": {
                #                    "answer": {
                #                       "type": "string",
                #                       "description": "Response content"
                #                    },
                #                    "mood": {
                #                        "type": "string",
                #                        "description": "Mood when responding"
                #                    }
                #                },
                #                "required": [
                #                    "answer",
                #                    "mood"
                #                ],
                #                "additionalProperties": False
                #            }
                #        }
                #   },
                #    "tools": api_tools if api_tools else None
                #    #"tool_choice": "auto"
                #},
                #json={ this for gpt-6-astra
                #    "model": "gpt-6-astra",
                #    "input": messages,
                #    "stream": False,
                #    "max_output_tokens": 10000,
                #    "reasoning": {
                #        "effort": "max"
                #    },
                #    "tools": api_tools if api_tools else None,
                #    "tool_choice": "auto"
                #},
                timeout=1200
            )
            response.raise_for_status()
            data = response.json()
            
            text, tool_call = self._extract_text_or_tool(data)
            # Если модель запросила инструмент — выполняем его
            if tool_call and tool_call['name'] in self.tools:
                logger.info(f"🔧 Tool use: {tool_call['name']}({tool_call['input']})")
                func = self.tools[tool_call['name']]['func']
                result = func(**tool_call['input'])
                    
                # Отправляем результат обратно в Claude
                messages.append({"role": "assistant", "content": data.get('content', [])})
                messages.append({
                    "role": "user", 
                    "content": f"Результат выполнения {tool_call['name']}: {result}"
                })
                    
                # Повторный запрос для получения финального текста
                second_response = requests.post(
                    f"{self.base_url}/claude/v1/messages",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-haiku-5-5",
                        "messages": messages,
                        "tool_choice": {"type": "none"},
                        "thinkingFlag": False,
                        "stream": False,
                        "max_tokens": 10000
                    }
                )
                second_response.raise_for_status()
                second_data = second_response.json()
                text, _ = self._extract_text_or_tool(second_data)
                
            if not text.strip():
                logger.warning(f"Пустой текст. Ответ: {json.dumps(data, ensure_ascii=False)[:300]}")
                return "Ошибка: агент не сгенерировал ответ"
                
            # Обновление контекста
            self.context.append({"role": "user", "content": prompt.strip()})
            self.context.append({"role": "assistant", "content": text})
                
            logger.info(f"✅ Ответ haiku: {text[:500]}...")
            return text
            #text = self._extract_text_or_tool(data) this worked for kimi
            #logger.info(f"📥 Ответ от claude haiku: {text[:200]}...")
            
            #if not text:
            #    logger.error(f"Пустой текст в ответе: {data}")
            #    return "Ошибка: агент не получил ответ от модели нет данных в data"
            
            # Обновление контекста
            #if text:
            #    self.context.append({"role": "user", "content": [{"type": "input_text", "text": prompt}]})
            #    self.context.append({"role": "assistant", "content": [{"type": "output_text", "text": text}]})
            
            #    #logger.info(f"✅ Ответ агента: {text[:1500]}...")
            #    return text
            
            #tool_call = self._extract_text_or_tool(data)
            # Если модель запросила инструмент — выполняем его
            #if tool_call:
            #    func_name = tool_call.get('name')
            #    # Парсим аргументы (могут быть JSON-строкой)
            #    args_str = tool_call.get('arguments', '{}')
            #    if isinstance(args_str, str):
            #        try:
            #            args = json.loads(args_str)
            #        except:
            #            args = {'query': args_str}
            #    else:
            #       args = args_str
            #        
            #    logger.info(f"🔧 Function call: {func_name}({args})")
                    
            #    if func_name in self.tools:
            #        func = self.tools[func_name]['func']
            #        try:
            #           result = func(**args)
            #            # Отправляем результат обратно в LLM для финального ответа
            #            messages.append({"role": "assistant", "content": [{"type": "output_text", "text": f"Calling {func_name}..."}]})
            #            messages.append({"role": "user", "content": [{"type": "input_text", "text": f"Result of {func_name}: {result}"}]})
            #                
            #            # Повторный запрос для получения человеческого ответа
            #            second_response = requests.post(
            #                f"{self.base_url}/openai/v1/responses",
            #                headers={
            #                    "Authorization": f"Bearer {self.api_key}",
            #                    "Content-Type": "application/json"
            #                },
            #                json={
            #                    "model": "kimi-k3",
            #                    "stream": False,
            #                    "input": messages,
            #                    "max_output_tokens": 10000,
            #                    "text": {
            #                        "format": {
            #                            "type": "json_schema",
            #                            "name": "basic_response",
            #                            "strict": True,
            #                            "schema": {
            #                                "type": "object",
            #                                "properties": {
            #                                    "answer": {
            #                                        "type": "string",
            #                                        "description": "Response content"
            #                                    },
            #                                    "mood": {
            #                                        "type": "string",
            #                                        "description": "Mood when responding"
            #                                    }
            #                                },
            #                                "required": [
            #                                    "answer",
            #                                    "mood"
            #                                ],
            #                                "additionalProperties": False
            #                            }
            #                        }
            #                    },
            #                    "tools": api_tools if api_tools else None
            #                    #"tool_choice": "auto"
            #                },
            #                timeout=1200
            #            )
            #            second_response.raise_for_status()
            #            second_data = second_response.json()
            #            final_text, _ = self._extract_text_or_tool(second_data)
                        #if final_text:
                        #    self.context.append({"role": "user", "content": [{"type": "input_text", "text": prompt}]})
                        #    self.context.append({"role": "assistant", "content": [{"type": "output_text", "text": final_text}]})
                        #    return text
            #            #return final_text or f"✅ {func_name} выполнен. Результат: {result}"
            #            if final_text:
            #                self.context.append({"role": "assistant", "content": [{"type": "output_text", "text": final_text}]})
            #                return final_text  # ✅ Возвращаем финальный, осмысленный ответ
            #        except Exception as e:
            #            return f"❌ Ошибка выполнения {func_name}: {str(e)}"
            #    else:
            #        return f"⚠️ Инструмент '{func_name}' не зарегистрирован"
            #text = self._extract_text_or_tool(data) this worked for gpt-6-astra

            #if not text:
            #    logger.error(f"Пустой текст в ответе: {data}")
            #    return "Ошибка: агент не сгенерировал ответ"
            
            #if text:
            #    # Обновление контекста
            #    #self.context.append({"role": "user", "content": [{"type": "text", "text": prompt}]}) format choices
            #    #self.context.append({"role": "assistant", "content": [{"type": "text", "text": text}]}) format choices
            #    self.context.append({"role": "user", "content": [{"type": "input_text", "text": prompt}]})
            #    self.context.append({"role": "assistant", "content": [{"type": "output_text", "text": text}]})
        
            #    logger.info(f"✅ Ответ агента: {text[:500]}...")
            #    return text
            
            #tool_call = self._extract_text_or_tool(data)
            # Если модель запросила инструмент — выполняем его
            #if tool_call:
            #    func_name = tool_call.get('name')
            #    # Парсим аргументы (могут быть JSON-строкой)
            #    args_str = tool_call.get('arguments', '{}')
            #    if isinstance(args_str, str):
            #        try:
            #            args = json.loads(args_str)
            #        except:
            #            args = {'query': args_str}
            #    else:
            #       args = args_str
            #        
            #    logger.info(f"🔧 Function call: {func_name}({args})")
            #        
            #    if func_name in self.tools:
            #        func = self.tools[func_name]['func']
            #        try:
            #            result = func(**args)
            #            # Отправляем результат обратно в LLM для финального ответа
            #            #messages.append({"role": "assistant", "content": [{"type": "text", "text": f"Calling {func_name}..."}]}) format choices
            #            #messages.append({"role": "user", "content": [{"type": "text", "text": f"Result of {func_name}: {result}"}]}) format choices
            #            messages.append({"role": "assistant", "content": [{"type": "output_text", "text": f"Calling {func_name}..."}]})
            #            messages.append({"role": "user", "content": [{"type": "input_text", "text": f"Result of {func_name}: {result}"}]})
                            
            #            # Повторный запрос для получения человеческого ответа
            #            second_response = requests.post(
            #                f"{self.base_url}/codex/v1/responses",
            #                headers={
            #                    "Authorization": f"Bearer {self.api_key}",
            #                    "Content-Type": "application/json"
            #                },
            #                json={
            #                    "model": "gpt-6-astra",
            #                    "input": messages,
            #                    "stream": False,
            #                    "max_output_tokens": 10000,
            #                    "reasoning": {
            #                        "effort": "max"
            #                    }
            #                },
            #                timeout=1200
            #            )
            #            second_response.raise_for_status()
            #            second_data = second_response.json()
            #            final_text, _ = self._extract_text_or_tool(second_data)
            #            if final_text:
            #                #self.context.append({"role": "user", "content": [{"type": "text", "text": prompt}]}) format choices
            #                #self.context.append({"role": "assistant", "content": [{"type": "text", "text": final_text}]}) format choices
            #                self.context.append({"role": "user", "content": [{"type": "input_text", "text": prompt}]})
            #                self.context.append({"role": "assistant", "content": [{"type": "output_text", "text": final_text}]})
            #                return text
            #            return final_text or f"✅ {func_name} выполнен. Результат: {result}"
            #        except Exception as e:
            #            return f"❌ Ошибка выполнения {func_name}: {str(e)}"
            #    else:
            #        return f"⚠️ Инструмент '{func_name}' не зарегистрирован"
        
        except requests.Timeout:
            logger.error("Таймаут запроса к API")
            return "Ошибка: таймаут соединения"
        except Exception as e:
            logger.error(f"Ошибка LLM: {str(e)}")
            return f"Ошибка: {str(e)}"

    def ask(self, service: str, requirements: str = "") -> str:
        # МЫ УБРАЛИ ЦИКЛ С REGEX! Теперь модель сама решит, когда использовать web_fetch, 
        # основываясь на SYSTEM_PROMPT и tool_choice="auto"
        prompt = f"""Создай production-ready интеграцию на Python для сервиса: "{service}"
            Дополнительные требования: "{requirements or 'Стандартная обёртка с auth, retry-логикой, типизацией и примерами'}"
            
            ДЕЙСТВУЙ СТРОГО ПО АЛГОРИТМУ ИЗ SYSTEM PROMPT. Сначала получи данные через web_fetch, затем выдай код.
        """
        return self._call_llm(prompt)

    #def ask(self, service: str, requirements: str = "") -> str: this worked
    #    prompt = f"""Создание production-ready интеграции на языке Python: 
    #        "{service}"
    #        Дополнительные требования: 
    #        "{requirements or "Стандартная обёртка с auth, retry-логикой, типизацией и примерами"}"
    #        
    #        ⚠️ КРИТИЧЕСКИ ВАЖНЫЙ АЛГОРИТМ ДЕЙСТВИЙ:
    #            1. Получить документацию с помощью инструмента 'web_fetch' на сайте сервиса.
    #            2. Сгенерировать полный, рабочий Python-код интеграции для Django/requests, по документации сервиса.
    #            3. Если не удалось написать код, указать причину в соответствии с форматом ответа.
    #        Формат:
    #            🎯 Краткое описание интеграции (service).
    #            📚 Инструкция по запуску (pip/npm, env, api, пример вызова).
    #            💡 Пример использования (requests, curl).
    #            🔗 Полный код класса-обёртки (python).
    #            🔍 Краткий анализ документации (примеры, первый вызов, ошибки, как начать, подсказки).
    #            ⚠️ Предупреждения о лимитах/безопасности (если они имеются).
    #    """

    #    # ✅ Простая логика использования инструментов
    #    for tool_name, tool_info in self.tools.items():
    #        if tool_name.lower() in prompt.lower():
    #            # Простой парсинг: ищем аргумент после двоеточия или в кавычках
    #            match = re.search(r'[:\s]+"([^"]+)"', prompt)
    #            arg = match.group(1) if match else prompt
    #            return tool_info['func'](arg)

    #    return self._call_llm(prompt)
        #1. Найти информацию с помощью инструмента 'web_search' о сервисе.
        #2. Получить документацию с помощью инструмента 'web_fetch' на сайте сервиса.
        #3. Посмотреть информацию с запросами (эндпоинты, auth, форматы запросов) в документации на сервисе.
        #4. Сгенерировать полный, рабочий Python-код интеграции для Django/requests, по документации сервиса.
        #5. Если не удалось написать код, указать причину в соответствии с форматом ответа.
        #6. НЕ ПИСАТЬ КОД НАУГАД, ВЕРНУТЬ ОТВЕТ, ФОРМАТ ОТВЕТА УКАЗАН.

    def generate_code(self, service_name: str) -> str:
        """Сгенерировать код интеграции по сервису"""
        prompt = f"""Ты — профессиональный разработчик на python. 
            Твоя задача — писать чистый, эффективный, хорошо документированный код.
            Отвечай ТОЛЬКО кодом, без лишних объяснений, если не запрошено иное.
            "{service_name}"
        """
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