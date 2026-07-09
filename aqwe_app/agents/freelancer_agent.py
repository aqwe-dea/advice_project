import os
import json
import requests
import logging
import re
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from .web_search import web_search
from .web_search import web_search as _web_search
from .web_fetch import web_fetch
from .wikipedia_search import search_by_wikipedia

logger = logging.getLogger(__name__)

class FreelancerAgent:
    """Агент-фрилансер: поиск заказов, авто-отклики, управление задачами"""
    
    SYSTEM_PROMPT = """
        Вы — Фрилансер АКВИ, эксперт по поиску и выполнению заказов.

        ЗАДАЧИ:
            1. Искать заказы по ссылкам указанных в разделе БИРЖИ фриланса по заданным критериям
            2. Фильтровать по навыкам, бюджету, срокам
            3. Генерировать персонализированные отклики (до 300 символов)
            4. Оценивать вероятность успеха
            5. Давать рекомендации по профилю

        БИРЖИ (используй их):
            1. https://www.upwork.com/nx/search/jobs/?q=python&sort=recency
            2. https://www.fl.ru/projects/category/programmirovanie/python/
            3. https://kwork.ru/projects?keyword=
            4. https://freelancehunt.com/projects/skill/python/151.html
            5. https://freelance.habr.com/tasks?q=
            6. https://workspace.ru/freelance/orders/?q=
            7. https://www.fiverr.com/search/gigs?query=
            8. https://www.freelancer.com/jobs/python/

        ИНСТРУМЕНТЫ:
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

        ФОРМАТ ОТВЕТА (СТРОГО):
            ## 🔍 Подходящие заказы
                | Платформа | Ссылка | Описание | Бюджет | Срок |
            ## ✍️ Шаблоны откликов
            [Персонализированный отклик до 300 символов]
            ## 📈 Вероятность успеха
            [низкая/средняя/высокая] + обоснование
            ## 💡 Рекомендации
            [Как улучшить профиль]

        ВАЖНО:
            - Отвечай НА РУССКОМ
            - Не выдумывай заказы, если поиск не дал результатов — честно сообщи
            - Используй инструменты, если они не доступны - честно сообщи
            - Если есть причина по которой инструменты не доступны, объясни или укажи на ошибку
            - Если поиск заказов не удался, сформируй остальные пункты отчета

        ФИЛОСОФИЯ:
            "Хороший отклик — это решение проблемы заказчика, а не список твоих навыков."
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai"): 
        self.api_key = api_key
        self.base_url = base_url
        self.context: List[Dict] = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]
        self.tools: Dict[str, Dict] = {}
    
    def add_tool(self, name: str, func: callable, description: str, parameters: Dict = None):
        self.tools[name] = {
            'func': func, 
            'description': description,
            'parameters': parameters or {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Запрос"}},
                "required": ["query"]
            }
        }
    
    def _build_claude_tools(self) -> List[Dict]:
        claude_tools = []
        for name, info in self.tools.items():
            claude_tools.append({
                "name": name,
                "description": info['description'],
                "input_schema": info['parameters']
            })
        return claude_tools
    
    def _extract_text_or_tool(self, data: dict) -> tuple[str, Optional[Dict]]:
        """Извлекает текст или tool_use из ответа Claude"""
        try:
            #content = data.get('content', [])
            #if not content or not isinstance(content, list):
            #    return "", None
            content = data.get('content', [])
            if not content:
                return "", None
            
            #first_block = content[0]
            
            #if not isinstance(first_block, dict):
            #    return str(first_block), None
            first_block = content[0] if isinstance(content, list) else content
            
            # Текстовый ответ
            #if first_block.get('type') == 'text':
            #    return first_block.get('text', ''), None
            # Случай 1: текстовый ответ
            if isinstance(first_block, dict) and first_block.get('type') == 'text':
                return first_block.get('text', ''), None
            
            # Tool use
            #if first_block.get('type') == 'tool_use':
            #    return "", {
            #        'id': first_block.get('id'),  # ← КРИТИЧНО: извлекаем id!
            #        'name': first_block.get('name'),
            #        'input': first_block.get('input', {})
            #    }
            
            # Случай 2: tool_use
            if isinstance(first_block, dict) and first_block.get('type') == 'tool_use':
                tool_info = {
                    'id': first_block.get('id'),  # ← КРИТИЧНО: извлекаем id!
                    'name': first_block.get('name'),
                    'input': first_block.get('input', {})
                }
                return "", tool_info

            # Фолбэк: попытка извлечь text напрямую
            text = first_block.get('text', '') if isinstance(first_block, dict) else str(first_block)
            return text, None

        except Exception as e:
            logger.error(f"Ошибка извлечения: {str(e)}")
            return "", None
    
    def _call_llm(self, prompt: str, max_retries: int = 2) -> str:
        for attempt in range(max_retries):
            messages = self.context.copy()
            messages.append({"role": "user", "content": prompt.strip()})
            
            claude_tools = self._build_claude_tools()

            try:
                response = requests.post(
                    f"{self.base_url}/claude/v1/messages",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-opus-4-7",
                        "messages": messages,
                        "thinkingFlag": False,
                        "stream": False,
                        "max_tokens": 10000,
                        "tools": [
                            {
                                "name": "web_search",
                                "description": "Ищет актуальную информацию в интернете. Используй для новостей, фактов, свежих данных.",
                                "input_schema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {"type": "string", "description": "Поисковый запрос"},
                                        "max_results": {"type": "integer", "default": 5},
                                    },
                                    "required": ["query"],
                                }
                            },
                            {
                                "name": "web_fetch",
                                "description": "Загружает веб-страницу и извлекает основной текст.",
                                "input_schema": {
                                    "type": "object",
                                    "properties": {
                                        "url": {"type": "string", "description": "Адрес страницы"},
                                        "max_length": {"type": "integer", "default": 5000},
                                    },
                                    "required": ["url"],
                                }
                            },
                            {
                                "name": "search_by_wikipedia",
                                "description": "Ищет статьи в Wikipedia и возвращает результаты.",
                                "input_schema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {"type": "string", "description": "Поисковый запрос"},
                                        "lang": {"type": "string", "description": "Язык Wikipedia"},
                                        "max_results": {"type": "integer", "default": 3},
                                    },
                                    "required": ["query"],
                                }
                            }
                        ],
                        "tool_choice": {"type": "auto"}  # ← Принудить использование инструментов
                        #"tools": claude_tools,
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                text, tool_call = self._extract_text_or_tool(data)
                
                # === Если модель запросила инструмент ===
                if tool_call and tool_call['name'] in self.tools:
                    logger.info(f"🔧 Tool use: {tool_call['name']}({tool_call['input']})")
                    
                    func = self.tools[tool_call['name']]['func']
                    #query = tool_call['input'].get('query', '')
                    result = func(**tool_call['input'])
                    
                    # Выполняем инструмент
                    #try:
                    #    tool_result = func(query)
                    #except Exception as e:
                    #    tool_result = f"Ошибка выполнения: {str(e)}"
                    
                    #logger.info(f"✅ Инструмент выполнен, результат: {tool_result[:200]}...")

                    # Отправляем результат обратно в Claude
                    messages.append({"role": "assistant", "content": data.get('content', [])})
                    messages.append({
                        "role": "user", 
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_call['id'],
                                "content": result
                            }
                        ]
                    })
                    
                    # === Формируем tool_result в формате Claude ===
                    #messages.append({
                    #    "role": "assistant",
                    #    "content": [data['content'][0]]  # Сохраняем original tool_use
                    #})
                    #messages.append({
                    #    "role": "user",
                    #    "content": [
                    #        {
                    #            "type": "tool_result",
                    #            "tool_use_id": tool_call['id'],  # ← КРИТИЧНО: передаём id!
                    #            "content": tool_result
                    #        }
                    #    ]
                    #})
                    
                    # === Повторный запрос для получения финального ответа ===
                    second_response = requests.post(
                        f"{self.base_url}/claude/v1/messages",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                            "anthropic-version": "2023-06-01"
                        },
                        json={
                            "model": "claude-opus-4-7",
                            "messages": messages,
                            "tool_choice": {"type": "auto"},
                            "thinkingFlag": False,
                            "stream": False,
                            "max_tokens": 10000
                        }
                    )
                    second_response.raise_for_status()
                    second_data = second_response.json()
                    
                    final_text, _ = self._extract_text_or_tool(second_data)
                    if final_text:
                        self.context.append({"role": "user", "content": prompt.strip()})
                        self.context.append({"role": "assistant", "content": final_text})
                        return final_text
                    
                    # Фолбэк
                    return f"✅ {tool_call['name']} выполнен. Данные: {result[:2000]}"
                
                # === Обычный текстовый ответ ===
                if text and text.strip():
                    self.context.append({"role": "user", "content": prompt.strip()})
                    self.context.append({"role": "assistant", "content": text})
                    return text
                
                logger.warning(f"Пустой ответ. Данные: {json.dumps(data, ensure_ascii=False)[:400]}")
                return "Ошибка: агент не сгенерировал ответ"
                
            except requests.Timeout:
                if attempt == max_retries - 1:
                    return "Ошибка: таймаут соединения"
                continue
            except Exception as e:
                logger.error(f"Ошибка LLM (попытка {attempt+1}): {str(e)}")
                if attempt == max_retries - 1:
                    return f"Ошибка: {str(e)}"
                continue
        
        return "Ошибка: исчерпаны попытки"
    
    def find_orders(self, skills: List[str], min_budget: int = 0, max_budget: int = None) -> str:
        skills_str = ", ".join(skills)
        budget_part = f" до {max_budget}" if max_budget else ""
        prompt = f"""
            Найди заказы для фрилансера с навыками: {skills_str}

            Бюджет: от {min_budget}{budget_part}

            ИНСТРУКЦИЯ:
                На основе полученных данных составь отчёт в формате из SYSTEM_PROMPT
            ВАЖНО: 
                Если инструменты доступны используй ПЕРЕД тем как давать финальный ответ.
        """
    
        return self._call_llm(prompt)
    
    def ask(self, question: str) -> str:
        for tool_name, tool_info in self.tools.items():
            if tool_name.lower() in question.lower():
                match = re.search(r'[:\s]+"([^"]+)"', question)
                arg = match.group(1) if match else question
                return tool_info['func'](arg)
        return self._call_llm(question)
    
    def web_search(query: str, max_results: int = 5) -> str:
        """Ищет информацию в интернете. Возвращает JSON с title/url/snippet."""
        return _web_search(query, max_results=max_results)
    
    def web_fetch(url: str, max_length: int = 5000) -> str:
        """Загружает веб-страницу и извлекает основной текст. JSON-строка с заголовком, текстом и метаданными."""
        return web_fetch(url, max_length=max_length)
    
    def search_by_wikipedia(query: str, lang: str = "ru", max_results: int = 3) -> str:
        """Ищет статьи в Wikipedia и возвращает результаты. JSON-строка со списком статей (заголовок, описание, url)."""
        return search_by_wikipedia(query, lang=lang, max_results=max_results)

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
            return f"[Hyperbrowse] {url}:\n{text[:2000]}..."
        except Exception as e:
            return f"[Hyperbrowse Error] {str(e)}"
    
    def clear_context(self):
        self.context = [{"role": "system", "content": self.SYSTEM_PROMPT}]
    
    def _googleSearch(self, query: str) -> str:
        """
            Для тестов: возвращаем реалистичные «данные поиска».
            В продакшене здесь должен быть вызов реального API (SerpAPI, Google Custom Search).
        """
        return f"""[googleSearch] Актуальные результаты по запросу "{query}":

            1. Upwork — Python Backend Developer (Remote)
            Ссылка: https://www.upwork.com/jobs/~01abc123
            Бюджет: $40-70/hr, Fixed-price $1500-3000
            Описание: Ищем разработчика для API на FastAPI, опыт с PostgreSQL, Docker.
            Срок: 1-3 месяца

            2. FL.ru — Fullstack (Python + React)
            Ссылка: https://www.fl.ru/projects/123456
            Бюджет: 50 000 - 120 000 ₽
            Описание: Разработка личного кабинета, бэкенд на Django, фронт на TypeScript.
            Срок: 2 месяца

            3. Kwork (Проекты) — Telegram Bot на Python
            Ссылка: https://kwork.ru/projects/789012
            Бюджет: 15 000 ₽
            Описание: Бот для приёма заказов, интеграция с CRM.
            Срок: 2 недели

            4. Habr Freelance — Data Parsing Script
            Ссылка: https://freelance.habr.com/tasks/987654
            Бюджет: 25 000 ₽
            Описание: Скрипт на Python для парсинга сайтов, выгрузка в CSV.
            Срок: 1 неделя

            ⚠️ Примечание: Это тестовые данные. В продакшене здесь будут реальные результаты API.
        """
    
    def _calculate(self, expression: str) -> str:
        try:
            allowed = {"__builtins__": {}}, {"add": lambda a,b: a+b, "sub": lambda a,b: a-b}
            result = eval(expression, *allowed)
            return f"Результат: {result}"
        except:
            return "Ошибка вычисления"
    
    