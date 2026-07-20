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

logger = logging.getLogger(__name__)

class InsiderAgent:
    """Агент-инсайдер: агрегация открытых данных, OSINT, структурирование информации"""
    
    SYSTEM_PROMPT = """
        Вы — Инсайдер АКВИ, эксперт по сбору и анализу открытых данных.

        ВАШИ ЗАДАЧИ:
            1. Агрегировать информацию из публичных источников (соцсети, сайты, реестры)
            2. Структурировать данные в читаемый отчёт (TXT/JSON/Markdown)
            3. Соблюдать этические границы: только публичные данные, без приватности
            4. Указывать источники и дату сбора для каждого факта
            5. Предлагать гипотезы на основе собранных данных

        ИНСТРУМЕНТЫ (ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙТЕ ИХ):
            - googleSearch(query: str): Ищите актуальную информацию по запросу. ВСЕГДА начинайте с поиска.
            - hyperbrowse(url: str, query: str): Посещайте конкретные страницы для извлечения деталей.

        ПРОЦЕСС РАБОТЫ:
            1. Сначала вызовите googleSearch для сбора данных по объекту
            2. При необходимости используйте hyperbrowse для углубления в конкретные источники
            3. На основе полученных данных составьте структурированный отчёт

        ФОРМАТ ОТВЕТА (СТРОГО СОБЛЮДАЙТЕ):
            ## 🔍 Резюме
            - [3-5 ключевых фактов]

            ## 📊 Детали
            [Подробный анализ по категориям]

            ## 🔗 Источники
            - [URL + дата доступа]

            ## ⚠️ Ограничения
            [Что не удалось проверить]

        ВАША ФИЛОСОФИЯ:
            "Знание — сила. Но сила требует ответственности."
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai/gemini/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.context: List[Dict] = [
            {"role": "user", "parts": [{"text": self.SYSTEM_PROMPT.strip()}]}
        ]
        self.tools: Dict[str, Dict] = {}
    
    def add_tool(self, name: str, func: callable, description: str):
        self.tools[name] = {'func': func, 'description': description}
    
    def _extract_text_from_response(self, data: dict) -> str:
        try:
            candidates = data.get('candidates', [])
            if candidates and isinstance(candidates, list) and len(candidates) > 0:
                candidate = candidates[0]
                content = candidate.get('content', {})
                parts = content.get('parts', [])
                if parts and isinstance(parts, list):
                    first_part = parts[0]
                    if isinstance(first_part, dict) and 'text' in first_part:
                        text = first_part.get('text', '')
                        if text.strip():
                            return text.strip()
            
            if 'text' in data and isinstance(data['text'], str):
                return data['text'].strip()
            
            if 'error' in data:
                logger.warning(f"API вернул ошибку: {data['error']}")
                return f"Ошибка API: {data['error']}"
            
            logger.warning(f"Не удалось извлечь текст. Полный ответ: {json.dumps(data, ensure_ascii=False)[:500]}")
            return ""
        except Exception as e:
            logger.error(f"Ошибка извлечения текста: {str(e)}")
            return ""
    
    def _call_llm(self, prompt: str, max_retries: int = 2) -> str:
        for attempt in range(max_retries):
            messages = self.context.copy()
            messages.append({"role": "user", "parts": [{"text": prompt.strip()}]})
            
            gemini_tools = []
            if self.tools:
                function_declarations = []
                for name, info in self.tools.items():
                    function_declarations.append({
                        "name": name,
                        "description": info['description'],
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {"query": {"type": "STRING", "description": "Запрос"}},
                            "required": ["query"]
                        }
                    })
                if function_declarations:
                    gemini_tools = [{"functionDeclarations": function_declarations}]
            
            try:
                response = requests.post(
                    f"{self.base_url}/models/gemini-3-5-flash:generateContent",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "contents": messages,
                        "tools": gemini_tools if gemini_tools else None,
                        "tool_config": {"function_calling_config": {"mode": "AUTO"}},  # ← Принудить использование инструментов
                        "generationConfig": {
                            "temperature": 0.2, 
                            "maxOutputTokens": 12000,  # ↑ Увеличили для длинных отчётов
                            "thinkingConfig": {
                                "includeThoughts": False,
                                "thinkingLevel": "high"
                            }
                        }
                    },
                    timeout=180
                )
                response.raise_for_status()
                data = response.json()
                
                candidates = data.get('candidates', [])
                if not candidates:
                    return "Ошибка: нет кандидатов в ответе API"
                
                candidate = candidates[0]
                content = candidate.get('content', {})
                parts = content.get('parts', [])
                
                if not parts:
                    return "Ошибка: пустые parts в ответе"
                
                first_part = parts[0]
                
                # ✅ СЛУЧАЙ 1: Обычный текстовый ответ
                if isinstance(first_part, dict) and 'text' in first_part:
                    text = first_part.get('text', '').strip()
                    if text:
                        self.context.append({"role": "user", "parts": [{"text": prompt.strip()}]})
                        self.context.append({"role": "model", "parts": [{"text": text}]})
                        logger.info(f"✅ Ответ: {text[:400]}...")
                        return text
                
                # ✅ СЛУЧАЙ 2: FunctionCall — выполняем инструмент
                if isinstance(first_part, dict) and 'functionCall' in first_part:
                    func_call = first_part['functionCall']
                    func_name = func_call.get('name')
                    func_args = func_call.get('args', {})
                    
                    logger.info(f"🔧 FunctionCall: {func_name}({func_args})")
                    
                    if func_name in self.tools:
                        tool_func = self.tools[func_name]['func']
                        query = func_args.get('query', '')
                        tool_result = tool_func(query)
                        
                        logger.info(f"✅ Инструмент выполнен: {tool_result[:200]}...")
                        
                        # Формируем промпт для генерации отчёта на основе данных
                        report_prompt = f"""
                            На основе следующих данных составь структурированный отчёт:

                            ДАННЫЕ ПОИСКА:
                                {tool_result[:8000]}  # ← Ограничили, чтобы не превысить лимит

                            ТРЕБОВАНИЯ К ОТЧЁТУ:
                                ## 🔍 Резюме (3-5 ключевых фактов)
                                ## 📊 Детали (по категориям)
                                ## 🔗 Источники (URL + дата)
                                ## ⚠️ Ограничения

                            Отвечай на русском, строго по формату.
                        """
                        # Повторный запрос для генерации отчёта
                        second_response = requests.post(
                            f"{self.base_url}/models/gemini-3-5-flash:generateContent",
                            headers={
                                "Authorization": f"Bearer {self.api_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "contents": [{"role": "user", "parts": [{"text": report_prompt}]}],
                                "generationConfig": {
                                    "temperature": 0.2, 
                                    "maxOutputTokens": 12000
                                }
                            },
                            timeout=180
                        )
                        second_response.raise_for_status()
                        second_data = second_response.json()
                        
                        final_text = self._extract_text_from_response(second_data)
                        if final_text:
                            self.context.append({"role": "user", "parts": [{"text": prompt.strip()}]})
                            self.context.append({"role": "model", "parts": [{"text": final_text}]})
                            return final_text
                        
                        # Фолбэк: форматируем сырые данные
                        return f"""## 🔍 Результаты поиска по запросу "{query}"

                            {tool_result[:4000]}

                            ⚠️ Примечание: Это сырые данные поиска. Для полного отчёта требуется дополнительная обработка.
                        """
                
                    else:
                        return f"⚠️ Инструмент '{func_name}' не зарегистрирован"
                
                logger.warning(f"Неизвестный формат parts: {first_part}")
                return "Ошибка: не удалось обработать ответ API"
                
            except requests.Timeout:
                if attempt == max_retries - 1:
                    return "Ошибка: таймаут соединения"
                continue
            except Exception as e:
                logger.error(f"Ошибка LLM (попытка {attempt+1}): {str(e)}")
                if attempt == max_retries - 1:
                    return f"Ошибка: {str(e)}"
                continue
        
        return "Ошибка: исчерпаны попытки выполнения запроса"
    
    def ask(self, subject: str, focus: str = "public_profile") -> str:
        focus_prompts = {
            "public_profile": "Собери публичную информацию: соцсети, упоминания в СМИ, профессиональные профили.",
            "company_research": "Исследуй компанию: сайт, отзывы, новости, реестры, финансовые данные (если публичные).",
            "topic_analysis": "Проанализируй тему: ключевые источники, мнения экспертов, тренды, противоречия."
        }
        prompt_focus = focus_prompts.get(focus, focus_prompts["public_profile"])
        
        # ← Исправлено: используем subject, который точно определён
        enhanced_prompt = f"""{prompt_focus}
            Объект: "{subject}"

            Требования:
                - Только публичные данные (без приватности)
                - Указывай источник и дату для каждого факта
                - Структурируй отчёт: резюме → детали → источники → ограничения
                - Будь объективен: отмечай неподтверждённую информацию

            Начни отчёт.
        """.strip()
        
        # ← Исправлено: проверяем tools по subject, который точно есть
        for tool_name, tool_info in self.tools.items():
            if tool_name.lower() in subject.lower():
                match = re.search(r'[:\s]+"([^"]+)"', subject)
                arg = match.group(1) if match else subject
                return tool_info['func'](arg)
        
        return self._call_llm(enhanced_prompt)
    
    def generate_report(self, subject: str, output_format: str = "markdown") -> str:
        prompt = f"""Создай структурированный отчёт об: "{subject}"
            Формат вывода: {output_format}

            Разделы:
                ## 🔍 Резюме (3-5 ключевых фактов)
                ## 📊 Детали (по категориям: профиль, деятельность, упоминания)
                ## 🔗 Источники (URL + дата доступа)
                ## ⚠️ Ограничения (что не удалось проверить)

            Важно:
                - Только публичные данные
                - Никакой приватной информации
                - Объективность и проверка фактов

            Начни отчёт.
        """.strip()
        return self._call_llm(prompt)
    
    def clear_context(self):
        self.context = [{"role": "user", "parts": [{"text": self.SYSTEM_PROMPT.strip()}]}]
    
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
            return f"[Hyperbrowse] {url}:\n{text[:5000]}..."
        except Exception as e:
            return f"[Hyperbrowse Error] {str(e)}"
    
    def _googleSearch(self, query: str) -> str:
        """
            Реализация поиска: для тестов возвращаем заглушку, 
            в продакшене здесь должен быть вызов реального API (Google Custom Search, SerpAPI и т.д.)
        """
        # Для тестов: имитация результатов поиска
        return f"""[googleSearch] Результаты по запросу "{query}":

            1. Официальный сайт: https://example.com/{query.replace(' ', '-')}
            - Последнее обновление: 2026-01-15
            - Кратко: Основная информация об объекте...

            2. Новости: https://news.example.com/search?q={query}
            - За последний месяц: 3 упоминания
            - Тональность: нейтральная

            3. Соцсети: 
            - Twitter/X: @example ({query})
            - LinkedIn: Компания "{query}"

            ⚠️ Это тестовые данные. В продакшене здесь будут реальные результаты API.
        """
    
    def _calculate(self, expression: str) -> str:
        try:
            allowed = {"__builtins__": {}}, {"add": lambda a,b: a+b, "sub": lambda a,b: a-b}
            result = eval(expression, *allowed)
            return f"Результат: {result}"
        except:
            return "Ошибка вычисления"