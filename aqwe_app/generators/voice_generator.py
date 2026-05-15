import logging
from .base import BaseGenerator
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class VoiceGenerator(BaseGenerator):
    """Генератор речи/голоса через KIE.ai"""
    
    DEFAULT_MODEL = "elevenlabs/text-to-speech-multilingual-v2"
    
    def generate(
        self,
        text: str,
        voice: str = "Rachel",
        stability: int = 0.5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Сгенерировать речь из текста.
        
        Returns:
            Dict с ключами:
            - success: bool
            - audio_url: str (если успешно)
            - error: str (если ошибка)
        """
        input_data = {
            "text": text,
            "voice": voice,
            "stability": stability
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
            "audio_url": result_urls[0],
            "text": text,
            "model": self.DEFAULT_MODEL
        }