import os
from .base import BaseGenerator
from typing import Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)

class VideoGenerator(BaseGenerator):
    """Генератор видео через KIE.ai"""
    DEFAULT_MODEL = "grok-imagine/text-to-video"
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Проверка валидности URL"""
        return bool(url and re.match(r'^https?://.+', url.strip()))
    
    def generate(
        self,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
            Сгенерировать короткое видео по промпту.
        
            Returns:
                Dict с ключами:
                    - success: bool
                    - video_url: str (если успешно)
                    - error: str (если ошибка)
        """
        # Валидация входных данных
        if not any([prompt.strip()]):
            return {"success": False, "error": "Нужно указать хотя бы один источник данных"}
        
        input_data = {
            "prompt": prompt.strip(),
            "aspect_ratio": "2:3",
            "mode": "normal",
            "duration": "6",
            "resolution": kwargs.get('resolution', '480p')
        }

        input_data.update({k: v for k, v in kwargs.items() if k not in input_data})
        logger.info(f"Запрос генерации видео: prompt={prompt[:50]}...")
        # Создание задачи
        task_id = self._create_task(self.DEFAULT_MODEL, input_data)
        if not task_id:
            logger.error("Не удалось создать задачу генерации видео")
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

        logger.info(f"✅ Видео сгенерировано: {first_url}")
        return {
            "success": True,
            "video_url": first_url,
            "prompt": prompt,
            "model": self.DEFAULT_MODEL,
            "metadata": {
                "resolution": input_data.get('resolution')
            }
        }