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

class ComposerAgent:
    """Агент-композитор: генерирует музыкальные концепции + интеграция с InstrumentalGenerator"""
    
    SYSTEM_PROMPT = """
        Вы — Композитор АКВИ, эксперт по созданию атмосферной музыки.
        
        ВАШИ ЗАДАЧИ:
        1. Создавать промпты для генерации музыки (Suno, KIE audio API)
        2. Комбинировать жанры: ambient + techno + dub + atmospheric beats
        3. Подбирать темп, тональность, инструменты под настроение
        4. Предлагать структуру трека: intro → build → drop → outro
        5. Давать рекомендации по пост-продакшену и экспорту
        
        ФОРМАТ ОТВЕТА:
        - Краткое описание концепции
        - Готовый промпт для аудио-API (в блоке кода)
        - Параметры: BPM, key, instruments, mood
        - Рекомендации по использованию (фон, медитация, контент)
        
        ВАША ФИЛОСОФИЯ:
        "Музыка — это энергия, которую можно почувствовать кожей."
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai/gemini/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.context: List[Dict] = [
            {"role": "user", "parts": [{"text": self.SYSTEM_PROMPT.strip()}]}
        ]
        self.tools: Dict[str, Dict] = {}
        self.instrumental_generator = None  # ← Будет установлен при интеграции
    
    def set_instrumental_generator(self, generator):
        """Установить генератор инструментальной музыки для pipeline"""
        self.instrumental_generator = generator
        logger.info("🎵 Instrumental generator подключён к ComposerAgent")
    
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
    
    def ask(self, mood: str, genre_mix: str = "ambient+techno+dub") -> str:
        prompt = f"""
            Создай музыкальную концепцию.
            Настроение: {mood}
            Жанры: {genre_mix}

            Верни:
                1. Описание атмосферы (2-3 предложения)
                2. Готовый промпт для Suno/KIE audio API в блоке кода
                3. Параметры: BPM, key, instruments, структура
                4. Рекомендации по использованию

            Пример промпта:
                "Create an atmospheric ambient techno track with dub elements, 110 BPM, D minor, featuring: warm pads, subtle rain sounds, deep sub-bass, delayed percussion, evolving textures. Structure: 30s intro → 60s build → 90s peak → 30s outro. Mood: meditative yet rhythmic, perfect for focus or relaxation."
        """.strip()

        # Проверка инструментов
        for tool_name, tool_info in self.tools.items():
            if tool_name.lower() in (mood or "").lower():
                match = re.search(r'[:\s]+"([^"]+)"', mood or "")
                arg = match.group(1) if match else (mood or "")
                return tool_info['func'](arg)

        return self._call_llm(prompt)
    
    def generate_prompt(self, title: str, duration: int = 180, bpm: int = 110) -> str:
        prompt = f"""
            Сгенерируй промпт для аудио-API.
            Название: "{title}"
            Длительность: {duration} сек
            Темп: {bpm} BPM

            Требования:
                - Стиль: ambient + techno + dub + atmospheric beats
                - Инструменты: pads, sub-bass, delayed percussion, field recordings
                - Структура: intro → build → drop → outro
                - Настроение: медитативное, но с ритмической основой

            Верни ТОЛЬКО готовый промпт в блоке кода, без лишних объяснений.
        """.strip()

        return self._call_llm(prompt)
    
    # === 🎵 НОВЫЙ МЕТОД: PIPELINE ГЕНЕРАЦИИ МУЗЫКИ ===
    def generate_music_pipeline(self, mood: str, genre_mix: str = "ambient+techno+dub") -> str:
        """
            Полный pipeline: Настроение → Концепция → Промпт → Генерация аудио → Результат
        
            Returns:
                str с текстовым ответом и ссылкой на аудио (или ошибкой)
        """

        logger.info(f"🎵 Запуск music pipeline: mood={mood}, genres={genre_mix}")
        
        # 1. Создаём музыкальную концепцию и промпт
        concept = self.ask(mood, genre_mix)
        if not concept or "ошибка" in concept.lower():
            return f"❌ Не удалось создать музыкальную концепцию: {concept}"
        
        # 2. Извлекаем промпт из концепции (ищем блок кода)
        prompt_match = re.search(r'```(?:text)?\s*(.*?)\s*```', concept, re.DOTALL)
        if prompt_match:
            audio_prompt = prompt_match.group(1).strip()
        else:
            # Фолбэк: используем mood как промпт
            audio_prompt = f"Create an atmospheric track with mood: {mood}, genres: {genre_mix}, 110 BPM, meditative yet rhythmic."
        
        logger.info(f"🎧 Промпт для аудио: {audio_prompt[:200]}...")
        
        # 3. Генерируем аудио (если генератор подключён)
        if not self.instrumental_generator:
            return f"{concept}\n\n⚠️ Instrumental generator не подключён. Аудио не создано."
        
        try:
            audio_result = self.instrumental_generator.generate(prompt=audio_prompt)
            
            if not audio_result.get('success'):
                return f"{concept}\n\n❌ Ошибка генерации: {audio_result.get('error')}"
            
            audio_url = audio_result.get('instrumental_url')
            
            # 4. Формируем финальный ответ
            final_response = f"""
                {concept}

                🎵 **Ваш трек:**
                    <audio controls src="{audio_url}"></audio>

                *Промпт:* "{audio_prompt}"
                *Модель:* {audio_result.get('metadata', {}).get('model', 'unknown')}
                *Длительность:* ~{audio_result.get('metadata', {}).get('duration', 'N/A')} сек
            """
            
            logger.info(f"✅ Аудио сгенерировано: {audio_url}")
            return final_response
            
        except Exception as e:
            logger.error(f"Ошибка генерации аудио: {str(e)}")
            return f"{concept}\n\n❌ Ошибка: {str(e)}"
    
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