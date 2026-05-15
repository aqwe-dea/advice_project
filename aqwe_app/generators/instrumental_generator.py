import requests
import json
from .base import BaseGenerator
from typing import Dict, Any, Optional

class InstrumentalGenerator(BaseGenerator):
    """Генератор инструментальной музыки через KIE.ai"""
    
    DEFAULT_MODEL = "ai-music-api/sounds"

    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate(
        self,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Сгенерировать инструментальной музыки по промпту.
        
        Returns:
            Dict с ключами:
            - success: bool
            - instrumental_url: str (если успешно)
            - error: str (если ошибка)
        """
        input_data = {
            "model": "V5",
            "prompt": prompt,
            "grabLyrics": False,
            "sound_loop": True,
            "sound_key": "F"
        }
        input_data.update(kwargs)
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/generate",
                headers=self.headers,
                json={
                    "model": DEFAULT_MODEL,
                    "input": input_data
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get('data', {}).get('taskId')
        except Exception as e:
            logger.error(f"Ошибка создания задачи: {str(e)}")
            return None
        
        #task_id = self._create_task(self.DEFAULT_MODEL, input_data)
        #if not task_id:
        #    return {"success": False, "error": "Не удалось создать задачу"}
        
        result = self._poll_task(task_id)
        if not result:
            return {"success": False, "error": "Задача не выполнена"}
        
        result_urls = result.get('resultUrls', [])
        if not result_urls:
            return {"success": False, "error": "Нет URL в результате"}
        
        return {
            "success": True,
            "instrumental_url": result_urls[0],
            "prompt": prompt,
            "model": self.DEFAULT_MODEL
        }