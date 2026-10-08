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
            # Вместо рискованного output[1].get('text'): пробую свой
            content_list = data.get('output')[1].get('content')

            if isinstance(content_list, list) and len(content_list) > 1:
                text = content_list[1].get('text', '')

            # Tool calls (современный формат)
            if 'tool_calls' in content_list and content_list['tool_calls']:
                tc = content_list['tool_calls'][0]
                return {
                    'id': tc.get('id'),
                    'name': tc['function']['name'],
                    'arguments': tc['function'].get('arguments', '{}')
                }
            # Legacy function_call
            if 'function_call' in content_list:
                fc = content_list['function_call'][0]
                return {
                    'id': fc.get('id'),
                    'name': fc.get('name'),
                    'arguments': fc.get('arguments', '{}')
                }
            elif isinstance(content_list, list) and len(content_list) > 0:
                text = content_list[0].get('text', '') # Фоллбэк на первый элемент
                return text

            else:
                text = str(content_list)
            
            logger.warning(f"Неизвестная структура ответа: {list(data.keys())}")
            return "", None
            
        except Exception as e:
            logger.error(f"Ошибка извлечения: {e} | Данные: {str(data)[:2000]}")
            return "", None
    #def _extract_text_or_tool(self, data: dict) -> tuple[str, Optional[Dict]]: this worked
    #    """
    #        Безопасно извлекает текст ИЛИ информацию о вызове инструмента из ответа API.
    #        Поддерживает: OpenAI/GPT/Grok (choices/output), Anthropic (content), Gemini (candidates).
    #        Returns: (текст, словарь tool_call или None)
    #    """
    #    try:
    #        # Вместо рискованного output[1].get('text'):
    #        content_list = data.get('output')[1].get('content')

    #        if isinstance(content_list, list) and len(content_list) > 1:
    #            text = content_list[1].get('text', '')

    #        elif isinstance(content_list, list) and len(content_list) > 0:
    #            # Tool calls (современный формат)
    #            if 'tool_calls' in content_list and content_list['tool_calls']:
    #                tc = content_list['tool_calls'][0]
    #                return {
    #                    'id': tc.get('id'),
    #                    'name': tc['function']['name'],
    #                    'arguments': tc['function'].get('arguments', '{}')
    #                }
    #            # Legacy function_call
    #            if 'function_call' in content_list:
    #                fc = content_list['function_call'][0]
    #                return {
    #                    'id': fc.get('id'),
    #                    'name': fc.get('name'),
    #                    'arguments': fc.get('arguments', '{}')
    #                }
    #            text = content_list[0].get('text', '') # Фоллбэк на первый элемент
    #            return text

    #        else:
    #            text = str(content_list)
    #        
    #        logger.warning(f"Неизвестная структура ответа: {list(data.keys())}")
    #        return "", None
            
    #    except Exception as e:
    #        logger.error(f"Ошибка извлечения: {e} | Данные: {str(data)[:2000]}")
    #        return "", None

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
                    "model": "gpt-6-astra",
                    "input": messages,
                    "stream": False,
                    "max_output_tokens": 10000,
                    "reasoning": {
                        "effort": "max"
                    },
                    "tools": api_tools if api_tools else None,
                    "tool_choice": "auto"
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
                                "model": "gpt-6-astra",
                                "input": messages,
                                "stream": False,
                                "max_output_tokens": 10000,
                                "reasoning": {
                                    "effort": "max"
                                },
                                "tools": api_tools if api_tools else None,
                                "tool_choice": "auto"
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

    def ask(self, service: str, requirements: str = "") -> str:
        prompt = f""" 
            Создайте production-ready интеграцию на языке Python для сервиса: "{service}"
            Дополнительные требования: "{requirements or "Стандартная обёртка с auth, retry-логикой, типизацией и примерами"}"
            
            ⚠️ КРИТИЧЕСКИ ВАЖНЫЙ АЛГОРИТМ ДЕЙСТВИЙ:
            1. Найти информацию с помощью инструмента 'web_search' о сервисе.
            2. Получить документацию с помощью инструмента 'web_fetch' на сайте сервиса.
            3. Посмотреть информацию с запросами (эндпоинты, auth, форматы запросов) в документации на сервисе.
            4. Сгенерировать полный, рабочий Python-код интеграции для Django/requests, по документации сервиса.
            5. Если не удалось написать код, указать причину в соответствии с форматом ответа.
            6. НЕ ПИСАТЬ КОД НАУГАД, ВЕРНУТЬ ОТВЕТ, ФОРМАТ ОТВЕТА УКАЗАН.    

            Формат:
                🎯 Краткое описание интеграции (service).
                📚 Инструкция по запуску (pip/npm, env, api, пример вызова).
                💡 Пример использования (requests, curl).
                🔗 Полный код класса-обёртки (python).
                🔍 Краткий анализ документации (примеры, первый вызов, ошибки, как начать, подсказки).
                ⚠️ Предупреждения о лимитах/безопасности (если они имеются).
        """

        # ✅ Простая логика использования инструментов
        for tool_name, tool_info in self.tools.items():
            if tool_name.lower() in prompt.lower():
                # Простой парсинг: ищем аргумент после двоеточия или в кавычках
                match = re.search(r'[:\s]+"([^"]+)"', prompt)
                arg = match.group(1) if match else prompt
                return tool_info['func'](arg)

        return self._call_llm(prompt)
    # def ask(self, service_name: str, requirements: str = "") -> str: this worked
    #    prompt = f"""
    #        Создай интеграцию для сервиса: "{service_name}"
    #        Требования: {requirements or "Стандартная обёртка с auth, retry, примерами"}

    #        Верни полный код, инструкцию по настройке и пример вызова.
    #    """

    #    # ✅ Простая логика использования инструментов
    #    for tool_name, tool_info in self.tools.items():
    #        if tool_name.lower() in prompt.lower():
    #            # Простой парсинг: ищем аргумент после двоеточия или в кавычках
    #            match = re.search(r'[:\s]+"([^"]+)"', prompt)
    #            arg = match.group(1) if match else prompt
    #            return tool_info['func'](arg)
        #for tool_name, tool_info in self.tools.items():
        #    if tool_name.lower() in prompt.lower():
        #        return tool_info['func'](prompt)

    #    return self._call_llm(prompt)

    def generate_code(self, service_name: str) -> str:
        """Сгенерировать код интеграции по сервису"""
        prompt = f""" 
            Задача: Создать интеграцию для сервиса "{service_name}".
            Требования: Стандартная обёртка с auth, retry, примерами, язык python, библиотека requests.
            Формат: Верни полный код, инструкцию по настройке и пример вызова.
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