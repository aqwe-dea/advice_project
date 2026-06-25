import os
import json
import requests
import logging
import re
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class FreelancerAgent:
    """Агент-фрилансер: поиск заказов, авто-отклики, управление задачами"""
    
    SYSTEM_PROMPT = """
        Вы — Фрилансер АКВИ, эксперт по поиску и выполнению заказов.

        ВАШИ ЗАДАЧИ:
            1. Парсить биржи фриланса (Upwork, FL.ru, Kwork) по заданным критериям
            2. Фильтровать заказы по навыкам, бюджету, срокам
            3. Генерировать персонализированные отклики
            4. Оценивать вероятность победы в конкурсе
            5. Напоминать о дедлайнах и коммуникации с заказчиками

        ФОРМАТ ОТВЕТА:
            - Список подходящих заказов (ссылка + краткое описание + бюджет)
            - Шаблон отклика для каждого заказа
            - Оценка вероятности успеха (низкая/средняя/высокая)
            - Рекомендации по улучшению профиля/портфолио

        ВАША ФИЛОСОФИЯ:
            "Хороший отклик — это решение проблемы заказчика, а не список твоих навыков."
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai/claude/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.context: List[Dict] = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]
        self.tools: Dict[str, Dict] = {}
    
    def add_tool(self, name: str, func: callable, description: str, parameters: Dict = None):
        """Добавить инструмент с описанием схемы параметров"""
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
        """Построить список инструментов в формате Claude API"""
        claude_tools = []
        for name, info in self.tools.items():
            claude_tools.append({
                "name": name,
                "description": info['description'],
                "input_schema": info['parameters']
            })
        return claude_tools
    
    def _extract_text_from_response(self, data: dict) -> tuple[str, Optional[Dict]]:
        """
            Извлечь текст или tool_use из ответа Claude.
            Returns: (text, tool_call_info or None)
        """
        try:
            content = data.get('content', [])
            if not content:
                return "", None
            
            first_block = content[0] if isinstance(content, list) else content
            
            # Случай 1: текстовый ответ
            if isinstance(first_block, dict) and first_block.get('type') == 'text':
                return first_block.get('text', ''), None
            
            # Случай 2: tool_use
            if isinstance(first_block, dict) and first_block.get('type') == 'tool_use':
                tool_info = {
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
        """Вызов Claude API с обработкой tool_use"""
        
        for attempt in range(max_retries):
            messages = self.context.copy()
            messages.append({"role": "user", "content": prompt.strip()})
            
            claude_tools = self._build_claude_tools()
            
            try:
                response = requests.post(
                    f"{self.base_url}/messages",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-opus-4-8",
                        "messages": messages,
                        "tools": claude_tools if claude_tools else None,
                        "thinkingFlag": False,
                        "stream": False,
                        "max_tokens": 10000
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ Claude ответ получен")
                
                text, tool_call = self._extract_text_from_response(data)
                
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
                        f"{self.base_url}/messages",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                            "anthropic-version": "2023-06-01"
                        },
                        json={
                            "model": "claude-opus-4-8",
                            "messages": messages,
                            "thinkingFlag": False,
                            "stream": False,
                            "max_tokens": 10000
                        }
                    )
                    second_response.raise_for_status()
                    second_data = second_response.json()
                    text, _ = self._extract_text_from_response(second_data)
                
                if not text.strip():
                    logger.warning(f"Пустой текст. Ответ: {json.dumps(data, ensure_ascii=False)[:300]}")
                    return "Ошибка: агент не сгенерировал ответ"
                
                # Обновление контекста
                self.context.append({"role": "user", "content": prompt.strip()})
                self.context.append({"role": "assistant", "content": text})
                
                logger.info(f"✅ Ответ: {text[:150]}...")
                return text
                
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
    
    def find_orders(self, skills: List[str], min_budget: int = 0, max_budget: int = None) -> str:
        skills_str = ", ".join(skills)
        prompt = f"""Найди заказы для фрилансера с навыками: {skills_str}
            Бюджет: от {min_budget}{" до " + str(max_budget) if max_budget else ""} руб.

            Источники: Upwork, FL.ru, Kwork, Telegram-каналы с заказами.

            Верни:
                ## 🔍 Подходящие заказы
                    | Платформа | Ссылка | Описание | Бюджет | Срок |
                    |-----------|--------|----------|--------|------|
                    | ... | ... | ... | ... | ... |

                ## ✍️ Шаблоны откликов
                    Для каждого заказа — персонализированный отклик (до 300 символов), который:
                    - Показывает понимание задачи
                    - Предлагает конкретное решение
                    - Включает призыв к действию

                ## 📈 Вероятность успеха
                    [низкая/средняя/высокая] с обоснованием

                ## 💡 Рекомендации
                    Как улучшить профиль/портфолио для повышения конверсии
        """
        
        return self._call_llm(prompt.strip())
    
    def ask(self, question: str) -> str:
        """Основной метод: задать вопрос агенту"""
        # Локальная проверка инструментов (fallback)
        for tool_name, tool_info in self.tools.items():
            if tool_name.lower() in question.lower():
                match = re.search(r'[:\s]+"([^"]+)"', question)
                arg = match.group(1) if match else question
                return tool_info['func'](arg)
        
        return self._call_llm(question)

    def _hyperbrowse(self, url: str, query: str = None) -> str:
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
        self.context = [{"role": "system", "content": self.SYSTEM_PROMPT}]
    
    def _googleSearch(self, query: str) -> str:
        return f"[googleSearch] Результаты по запросу '{query}': пример ответа."
    
    def _calculate(self, expression: str) -> str:
        try:
            allowed = {"__builtins__": {}}, {"add": lambda a,b: a+b, "sub": lambda a,b: a-b}
            result = eval(expression, *allowed)
            return f"Результат: {result}"
        except:
            return "Ошибка вычисления"