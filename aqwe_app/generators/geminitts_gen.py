from .base import BaseGenerator
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from pathlib import Path
from abc import abstractmethod
import logging
import re

logger = logging.getLogger(__name__)

class GeminittsGen(BaseGenerator):
    """Создание голоса по тексту через KIE.ai"""
    
    DEFAULT_MODEL = "google/gemini-3-8-flash-tts"
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Проверка валидности URL"""
        return bool(url and re.match(r'^https?://.+', url.strip()))

    def generate(
        self,
        text1: str,
        text2: str,
        #text3: str,
        #text4: str,
        #text5: str,
        #nika1: str = "Nyla",
        #kira2: str = "Enya",
        filler_words: bool = True,
        temperature: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
            Отредактировать изображение.
        
            Returns:
                Dict с ключами:
                    - success: bool
                    - geminitts_url: str (если успешно)
                    - error: str (если ошибка)
        """

        # Валидация входных данных
        #if not any([text1.strip(), text2.strip()]):
        #    return {"success": False, "error": "Нужно указать хотя бы один источник данных"}
        
        input_data = {
            "speakers": [
                {
                    "speaker_id": "Speaker 1",
                    "voice_name": "Leda"
                },
                {
                    "speaker_id": "Speaker 2",
                    "voice_name": "Veda"
                }
            ],
            "dialogue_turns": [
                {
                    "speaker_id": "Speaker 1",
                    "style": "commanding, rich vocal modulation, dramatic pauses",
                    "text": text1.strip()
                },
                {
                    "speaker_id": "Speaker 2",
                    "style": "High energy, elongated vowels",
                    "text": text2.strip()
                }
                #{
                #    "speaker_id": "Speaker 1",
                #    "style": "Calm, measured delivery",
                #    "text": text3.strip()
                #},
                #{
                #    "speaker_id": "Speaker 2",
                #    "style": "whisper quietly",
                #    "text": text4.strip()
                #},
                #{
                #    "speaker_id": "Speaker 1",
                #    "style": "Warm and neutral delivery with micro-pauses",
                #    "text": text5.strip()
                #}
            ],
            "filler_words": filler_words,
            "temperature": temperature
        }

        input_data.update({k: v for k, v in kwargs.items() if k not in input_data})
        logger.info(f"Запрос голоса: text1={text1[:50]}...")
        # Создание задачи
        task_id = self._create_task(self.DEFAULT_MODEL, input_data)
        if not task_id:
            logger.error("Не удалось создать задачу на редактирование изображения")
            return {"success": False, "error": "Не удалось создать задачу"}
        
        logger.info(f"Задача создана: task_id={task_id}")
         # Опрос задачи
        result = self._poll_task(task_id)
        if not result:
            logger.error("Задача не выполнена или таймаут")
            return {"success": False, "error": "Задача не выполнена"}
        
        # Извлечение URL с поддержкой разных форматов ответа
        result_urls = (
            result.get('resultUrls') or 
            result.get('outputUrls') or 
            (result.get('data', {}).get('resultUrls') if isinstance(result.get('data'), dict) else None) or
            []
        )
        
        if not result_urls:
            logger.error(f"Нет URL в результате: {result}")
            return {"success": False, "error": "Нет URL в результате"}
        
        # Валидация первого URL
        first_url = result_urls[0].strip() if isinstance(result_urls[0], str) else None
        if not self._is_valid_url(first_url):
            logger.warning(f"Невалидный URL: {first_url}")
            return {"success": False, "error": "Невалидный URL в результате"}
        
        logger.info(f"✅ Речь создана: {first_url}")
        return {
            "success": True,
            "geminitts_url": first_url,
            "text1": text1,
            "text2": text2,
            "model": self.DEFAULT_MODEL
        }