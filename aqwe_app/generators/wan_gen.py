from .base import BaseGenerator
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from pathlib import Path
from abc import abstractmethod
import logging
import re

logger = logging.getLogger(__name__)

class WanGen(BaseGenerator):
    """Создатель видео через KIE.ai"""
    
    DEFAULT_MODEL = "wan/3-0-video"
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Проверка валидности URL"""
        return bool(url and re.match(r'^https?://.+', url.strip()))

    def generate(
        self,
        prompt: str, # prompt 20000 character
        first_frame_url: str = "",
        last_frame_url: str = "",
        reference_image_urls: str = "",
        reference_link_urls: str = "",
        reference_audio_urls: str = "",
        reference_video_urls: str = "",
        reference_file_urls: str = "",
        duration: int = 30,
        seed: int = 0,
        audio: bool = True,
        nsfw_checker: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
            Отредактировать изображение.
        
            Returns:
                Dict с ключами:
                    - success: bool
                    - wan_url: str (если успешно)
                    - error: str (если ошибка)
        """

        # Валидация входных данных
        if not any([prompt.strip(), reference_image_urls.strip(), first_frame_url.strip(), reference_link_urls.strip(), reference_audio_urls.strip(), reference_video_urls.strip()]):
            return {"success": False, "error": "Нужно указать хотя бы один источник данных"}
        
        input_data = {
            "prompt": prompt.strip(),
            "first_frame_url": first_frame_url.strip(),
            "last_frame_url": last_frame_url.strip(),
            "reference_image_urls": reference_image_urls.strip(),
            "reference_link_urls": reference_link_urls.strip(),
            "reference_audio_urls": reference_audio_urls.strip(),
            "reference_video_urls": reference_video_urls.strip(),
            "reference_file_urls": reference_file_urls.strip(),
            "aspect_ratio": "1:1",
            "resolution": "480P",
            "duration": duration,
            "audio": audio,
            "seed": seed,
            "nsfw_checker": nsfw_checker
        }

        input_data.update({k: v for k, v in kwargs.items() if k not in input_data})
        logger.info(f"Запрос видео: prompt={prompt[:50]}...")
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
        
        logger.info(f"✅ Изображение отредактировано: {first_url}")
        return {
            "success": True,
            "wan_url": first_url,
            "prompt": prompt,
            "model": self.DEFAULT_MODEL,
            "metadata": {
                "image_url": reference_image_urls if reference_image_urls else None
            }
        }