from .base import BaseGenerator
from typing import Dict, Any, Optional

class LiveimageGenerator(BaseGenerator):
    """Генератор живых изображений через KIE.ai"""
    
    DEFAULT_MODEL = "kling/v2-1-standard"
    
    def generate(
        self,
        prompt: str,
        negative_prompt: str = "bad, ugly, distorted, low quality",
        image_url: str = "",
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
        input_data = {
            "prompt": prompt,
            "image_url": image_url,
            "duration": "5",
            "negative_prompt": negative_prompt,
            "cfg_scale": 0.5,
            "nsfw_checker": False
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
            "liveimage_url": result_urls[0],
            "prompt": prompt,
            "model": self.DEFAULT_MODEL
        }