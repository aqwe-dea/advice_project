import os
import logging
from .base import BaseGenerator
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class VideoGenerator(BaseGenerator):
    """Генератор видео через KIE.ai"""
    
    DEFAULT_MODEL = "grok-imagine/text-to-video"
    
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
        input_data = {
            "prompt": prompt,
            "aspect_ratio": "2:3",
            "mode": "normal",
            "duration": "6",
            "resolution": "480p"
        }
        input_data.update(kwargs)
        
        task_id = self._create_task(self.DEFAULT_MODEL, input_data)
        if not task_id:
            return {"success": False, "error": "Не удалось создать задачу"}
        
        result = self._poll_task(task_id)
        if not result:
            return {"success": False, "error": "Задача не выполнена"}
        
        result_urls = result.get('resultUrls', [])
        if not result_urls:
            return {"success": False, "error": "Нет URL в результате"}
        
        return {
            "success": True,
            "video_url": result_urls[0],
            "prompt": prompt,
            "model": self.DEFAULT_MODEL
        }