import os
import json
import requests
import logging
import re
from typing import List, Optional, Dict
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class DirectorAgent:
    """Агент-режиссёр: создаёт сценарии, концепции видео, тренд-анализ"""
    
    SYSTEM_PROMPT = """
        Вы — Режиссёр АКВИ, эксперт по созданию увлекательного видеоконтента.
        
        ВАШИ ЗАДАЧИ:
        1. Писать сценарии для коротких роликов (TikTok, Reels, YouTube Shorts)
        2. Анализировать тренды и предлагать актуальные темы
        3. Создавать концепции визуального стиля (цвет, ритм, монтаж)
        4. Предлагать структуру: хук → развитие → кульминация → CTA
        5. Сохранять эмпатию и креативность в общении
        
        ФОРМАТ ОТВЕТА:
        - Краткая концепция (1-2 предложения)
        - Подробный сценарий с таймингом
        - Рекомендации по визуалу и звуку
        - Хештеги и CTA для публикации
        
        ВАША ФИЛОСОФИЯ:
        "Хорошее видео — это история, которую хочется досмотреть до конца."
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
            # Формат 1: candidates[0].content.parts[0].text
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
            
            # Формат 2: прямой text в корне (некоторые эндпоинты)
            if 'text' in data and isinstance(data['text'], str):
                return data['text'].strip()
            
            # Формат 3: error-сообщение
            if 'error' in data:
                logger.warning(f"API вернул ошибку: {data['error']}")
                return f"Ошибка API: {data['error']}"
            
            # Логирование для отладки
            logger.warning(f"Не удалось извлечь текст. Полный ответ: {json.dumps(data, ensure_ascii=False)[:500]}")
            return ""
            
        except Exception as e:
            logger.error(f"Ошибка извлечения текста: {str(e)}")
            return ""
    
    def _call_llm(self, prompt: str, max_retries: int = 2) -> str:
        """Вызов LLM с обработкой functionCall"""
    
        for attempt in range(max_retries):
            messages = self.context.copy()
            messages.append({"role": "user", "parts": [{"text": prompt.strip()}]})
        
            # Формирование tools
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
                        "generationConfig": {
                            "temperature": 0.2, 
                            "maxOutputTokens": 10000,
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
            
                # === ОБРАБОТКА ОТВЕТА ===
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
                        # Обновляем контекст
                        self.context.append({"role": "user", "parts": [{"text": prompt.strip()}]})
                        self.context.append({"role": "model", "parts": [{"text": text}]})
                        logger.info(f"✅ Ответ: {text[:150]}...")
                        return text
            
                # ✅ СЛУЧАЙ 2: FunctionCall — выполняем инструмент
                if isinstance(first_part, dict) and 'functionCall' in first_part:
                    func_call = first_part['functionCall']
                    func_name = func_call.get('name')
                    func_args = func_call.get('args', {})
                
                    logger.info(f"🔧 FunctionCall: {func_name}({func_args})")
                
                    # Выполняем инструмент, если он зарегистрирован
                    if func_name in self.tools:
                        tool_func = self.tools[func_name]['func']
                        query = func_args.get('query', '')
                        tool_result = tool_func(query)
                    
                        logger.info(f"✅ Инструмент выполнен: {tool_result[:100]}...")
                    
                        # Отправляем результат обратно в LLM для финального ответа
                        messages.append({"role": "model", "parts": [first_part]})  # functionCall
                        messages.append({"role": "function", "parts": [{
                            "functionResponse": {
                                "name": func_name,
                                "response": {"result": tool_result}
                            }
                        }]})
                    
                        # Повторный запрос для получения текстового ответа
                        second_response = requests.post(
                            f"{self.base_url}/models/gemini-3-5-flash:generateContent",
                            headers={
                                "Authorization": f"Bearer {self.api_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "contents": messages,
                                "generationConfig": {
                                    "temperature": 0.2, 
                                    "maxOutputTokens": 10000,
                                    "thinkingConfig": {
                                        "includeThoughts": False,
                                        "thinkingLevel": "high"
                                    }
                                }
                            },
                            timeout=180
                        )
                        second_response.raise_for_status()
                        second_data = second_response.json()
                    
                        # Извлекаем финальный текст
                        second_candidates = second_data.get('candidates', [])
                        if second_candidates:
                            second_content = second_candidates[0].get('content', {})
                            second_parts = second_content.get('parts', [])
                            if second_parts and isinstance(second_parts[0], dict) and 'text' in second_parts[0]:
                                final_text = second_parts[0].get('text', '').strip()
                                if final_text:
                                    self.context.append({"role": "user", "parts": [{"text": prompt.strip()}]})
                                    self.context.append({"role": "model", "parts": [{"text": final_text}]})
                                    return final_text
                    
                        # Фолбэк: возвращаем результат инструмента
                        return f"🔍 Результаты поиска:\n{tool_result}"
                
                    else:
                        return f"⚠️ Инструмент '{func_name}' не зарегистрирован"
            
                # ❌ Неизвестный формат
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
    
    def ask(self, question: str, platform: str = "universal") -> str:
        platform_prompt = {
            "tiktok": "Создай сценарий для TikTok (15-60 сек, вертикальный формат, быстрый хук).",
            "reels": "Создай сценарий для Instagram Reels (до 90 сек, эстетика + тренды).",
            "youtube": "Создай сценарий для YouTube Shorts (до 60 сек, образовательный/развлекательный).",
            "universal": "Создай универсальный сценарий, адаптируемый под любые платформы."
        }
        
        prompt_prefix = platform_prompt.get(platform, platform_prompt["universal"])
        enhanced_prompt = f"{prompt_prefix}\n\nЗапрос: {question}".strip()
        
        for tool_name, tool_info in self.tools.items():
            if tool_name.lower() in subject.lower():
                match = re.search(r'[:\s]+"([^"]+)"', subject)
                arg = match.group(1) if match else subject
                return tool_info['func'](arg)
        
        return self._call_llm(enhanced_prompt)
    
    def generate_script(self, topic: str, duration: int = 30) -> str:
        prompt = f"""Создай сценарий видео на тему: "{topic}"
            Длительность: {duration} секунд

            Формат:
                🎬 Хук (0-3 сек): цепляющая фраза/визуал
                📖 Развитие (3-{duration-10} сек): суть, эмоция, динамика
                💥 Кульминация ({duration-10}-{duration-5} сек): пик, инсайт, поворот
                🎯 CTA ({duration-5}-{duration} сек): призыв к действию

            Добавь:
                - Рекомендации по визуалу (цвет, ракурс, монтаж)
                - Подборку хештегов (5-7 шт)
                - Идеи для звука/музыки

            Ответь на русском, с форматированием.
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
            return f"[Hyperbrowse] {url}:\n{text[:1000]}..."
        except Exception as e:
            return f"[Hyperbrowse Error] {str(e)}"
    
    def _googleSearch(self, query: str) -> str:
        return f"[googleSearch] Результаты по запросу '{query}': пример ответа."