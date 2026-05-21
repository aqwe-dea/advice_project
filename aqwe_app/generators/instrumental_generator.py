import os
import requests
import logging
import json
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class InstrumentalGenerator:
    """Генератор инструментальной музыки через KIE.ai"""

    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _create_task(self, input_data: Dict[str, Any]) -> Optional[str]:
        """Создать задачу генерации, вернуть taskId"""
        try:
            # ✅ Правильный формат запроса: param = JSON-строка
            #param_str = json.dumps(input_data)
            
            response = requests.post(
                f"{self.base_url}/generate",
                headers=self.headers,
                json=input_data
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Полный ответ API: {data}")

            # ✅ taskId находится в data['data']['taskId']
            return data.get('data', {}).get('taskId')
        except Exception as e:
            logger.error(f"Ошибка создания задачи: {str(e)} or {data}")
            return None
    
    def _poll_task(self, task_id: str, max_wait: int = 600) -> Optional[Dict[str, Any]]:
        """Опрос задачи до завершения (макс. 10 минут)"""
        start = time.time()
        
        while time.time() - start < max_wait:
            try:
                response = requests.get(
                    f"{self.base_url}/generate/record-info",
                    headers=self.headers,
                    params={"taskId": task_id}
                )
                response.raise_for_status()
                data = response.json().get('data', {})
                logger.info(f"Что в ответе содержит строчка data: {data}")
                # Статус находится в data['status']
                if data.get('status') == 'SUCCESS':
                    # Результат находится в data['data']['response']
                    response_data = data.get('response', {})
                    return {
                        'sunoData': response_data.get('sunoData', [])
                    }
                elif data.get('status') == 'fail':
                    logger.error(f"Задача не выполнена: {data.get('failMsg')} or {data}")
                    return None
                
                time.sleep(10)
            except Exception as e:
                logger.error(f"Ошибка опроса: {str(e)} or {data}")
                time.sleep(10)
        
        logger.error("Превышено время ожидания задачи")
        return None

    def generate(
        self,
        prompt: str,
        model: str = "V5",
        callBackUrl: str = "https://api.kie.ai/callback",
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
            "prompt": prompt,
            "customMode": False,
            "instrumental": True,
            "model": model,
            "callBackUrl": callBackUrl,
            "style": "Electronic",
            "title": "Enjoy Meditation",
            "vocalGender": "f"
        }
        input_data.update(kwargs)

        task_id = self._create_task(input_data)
        if not task_id:
            return {"success": False, "error": "Не удалось создать задачу"}

        result = self._poll_task(task_id)
        if not result:
            return {"success": False, "error": "Задача не выполнена"}
        
        # Извлекаем URL из sunoData
        suno_data = result.get('sunoData', [])
        if not suno_data:
            return {"success": False, "error": "Нет данных в результате"}
        
        # Берем первый элемент
        first_result = suno_data[0]
        audio_url = first_result.get('audioUrl', '')
        
        if not audio_url:
            return {"success": False, "error": "Нет audioUrl в результате"}
        
        return {
            "success": True,
            "instrumental_url": audio_url,
            "prompt": prompt
        }