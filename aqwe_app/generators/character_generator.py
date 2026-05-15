from .base import BaseGenerator
from typing import Dict, Any, Optional

class CharacterGenerator(BaseGenerator):
    """Генератор персонажей через KIE.ai"""
    
    DEFAULT_MODEL = "kling/ai-avatar-pro"
    
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
        input_data = {
            "prompt": prompt,
            "image_url": image_url,
            "audio_url": audio_url
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
            "character_url": result_urls[0],
            "prompt": prompt,
            "model": self.DEFAULT_MODEL
        }