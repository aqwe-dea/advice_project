from .base import BaseGenerator
from typing import Dict, Any, Optional

class ImageEdit(BaseGenerator):
    """Редактор изображений через KIE.ai"""
    
    DEFAULT_MODEL = "gpt-image-2-image-to-image"
    
    def generate(
        self,
        prompt: str,
        input_urls: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Отредактировать изображение.
        
        Returns:
            Dict с ключами:
            - success: bool
            - edit_url: str (если успешно)
            - error: str (если ошибка)
        """
        input_data = {
            "prompt": prompt,
            "input_urls": input_urls,
            "aspect_ratio": "auto",
            "resolution": "1K"
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
            "edit_url": result_urls[0],
            "prompt": prompt,
            "model": self.DEFAULT_MODEL
        }