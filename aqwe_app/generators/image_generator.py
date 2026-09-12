from .base import BaseGenerator
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from pathlib import Path
from abc import abstractmethod

class ImageGenerator(BaseGenerator):
    """Генератор изображений через KIE.ai + FLUX.1"""
    
    DEFAULT_MODEL = "gpt-image-2-5-flare-text-to-image"
    
    def generate(
        self,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Сгенерировать изображение по промпту.
        
        Returns:
            Dict с ключами:
            - success: bool
            - image_url: str (если успешно)
            - error: str (если ошибка)
        """
        input_data = {
            "prompt": prompt,
            "aspect_ratio": "1:1",
            "resolution": "4K",
            "background": "auto"
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
            "image_url": result_urls[0],
            "prompt": prompt,
            "model": self.DEFAULT_MODEL
        }