from .base import BaseGenerator
from typing import Dict, Any, Optional

class CharacterGenerator(BaseGenerator):
    """Генератор персонажей через KIE.ai"""
    
    DEFAULT_MODEL = "infinitalk/from-audio"
    
    def generate(
        self,
        prompt: str,
        image_url: str = "",
        audio_url: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Сгенерировать персонажа по промпту изображению и аудио.
        
        Returns:
            Dict с ключами:
            - success: bool
            - character_url: str (если успешно)
            - error: str (если ошибка)
        """
        # Проверка, что хотя бы один из источников данных присутствует
        if not prompt and not image_url and not audio_url:
            return {"success": False, "error": "Нужно указать хотя бы один источник данных"}
        
        input_data = {
            "prompt": prompt,
            "image_url": image_url,
            "audio_url": audio_url,
            "resolution": "480p"
        }
        input_data.update(kwargs)
        
        # Используем правильный endpoint для генерации персонажей
        task_id = self._create_task(self.DEFAULT_MODEL, input_data)
        if not task_id:
            return {"success": False, "error": "Не удалось создать задачу"}
        
        result = self._poll_task(task_id)
        if not result:
            return {"success": False, "error": "Задача не выполнена"}
        
        # Проверка на наличие результатов
        result_urls = result.get('resultUrls', [])
        if not result_urls:
            # Попробуем другой ключ, возможно, структура ответа отличается
            result_urls = result.get('outputUrls', [])
        
        if not result_urls:
            return {"success": False, "error": "Нет URL в результате"}
        
        return {
            "success": True,
            "character_url": result_urls[0],
            "prompt": prompt,
            "model": self.DEFAULT_MODEL
        }