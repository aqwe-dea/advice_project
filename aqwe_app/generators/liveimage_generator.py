import os
from .base import BaseGenerator
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from pathlib import Path
from abc import abstractmethod
import logging
import re

logger = logging.getLogger(__name__)

class LiveimageGenerator(BaseGenerator):
    """Генератор живых изображений через KIE.ai"""
    DEFAULT_MODEL = "google/gemini-omni-flash-1-2"
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Проверка валидности URL"""
        return bool(url and re.match(r'^https?://.+', url.strip()))
    
    def generate(
        self,
        prompt: str, # prompt 20000 character
        image_urls: list,
        video_list: list,
        character_ids: list,
        first_frame_url: str = "",
        last_frame_url: str = "",
        duration: int = 4,
        seeds: int = 10000,
        **kwargs
    ) -> Dict[str, Any]:
        """
            Сгенерировать живое изображение по промпту.
        
            Returns:
                Dict с ключами:
                    - success: bool
                    - liveimage_url: str (если успешно)
                    - error: str (если ошибка)
        """

        # Валидация входных данных
        if not any([prompt.strip(), image_urls.strip()]):
            return {"success": False, "error": "Нужно указать хотя бы один источник данных"}
        
        input_data = {
            "prompt": prompt.strip(),
            "image_urls": image_urls,
            "first_frame_url": first_frame_url.strip(),
            "last_frame_url": last_frame_url.strip(),
            "video_list": video_list,
            "duration": duration,
            "aspect_ratio": "16:9",
            "character_ids": character_ids,
            "resolution": "360p",
            "seeds": seeds
        }

        input_data.update({k: v for k, v in kwargs.items() if k not in input_data})
        logger.info(f"Запрос генерации живого изображения: prompt={prompt[:50]}...")
        # Создание задачи
        task_id = self._create_task(self.DEFAULT_MODEL, input_data)
        if not task_id:
            logger.error("Не удалось создать задачу генерации живого изображения")
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
        
        logger.info(f"✅ Живое изображение сгенерировано: {first_url}")
        return {
            "success": True,
            "liveimage_url": first_url,
            "prompt": prompt,
            "model": self.DEFAULT_MODEL
        }