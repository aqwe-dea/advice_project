import os
import requests
import logging
import json
import time
import re
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

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Проверка валидности URL"""
        return bool(url and re.match(r'^https?://.+', url.strip()))
    
    def _create_task(self, input_data: Dict[str, Any]) -> Optional[str]:
        """Создать задачу генерации, вернуть taskId"""
        try:
             # ✅ KIE.ai ожидает param как JSON-строку
            # "param": param_str,
            # "type": kwargs.get('type', 'chirp-crow'),
            # "operationType": "generate" 
            # param_str = json.dumps(input_data)
            response = requests.post(
                f"{self.base_url}/generate",
                headers=self.headers,
                json=input_data
            )

            response.raise_for_status()
            data = response.json()
            logger.info(f"Полный ответ API: {data}, Создание задачи: статус={data.get('code')}, taskId={data.get('data', {}).get('taskId')}")
            return data.get('data', {}).get('taskId')
        except Exception as e:
            logger.error(f"Ошибка создания задачи: {str(e)}{data}")
            return None
    
    def _poll_task(self, task_id: str, max_wait: int = 900) -> Optional[Dict[str, Any]]:
        """Опрос задачи до завершения (макс. 15 минут)"""
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
                if data.get('status') == 'SUCCESS':
                    # Поддержка разных структур ответа
                    suno_data = (
                        data.get('response', {}).get('sunoData') or
                        data.get('sunoData') or
                        data.get('data', {}).get('response', {}).get('sunoData') or
                        []
                    )

                    logger.info(f"✅ Задача выполнена: {len(suno_data)} результатов")
                    return {'sunoData': suno_data}
                
                elif data.get('status') == 'fail':
                    logger.error(f"Задача не выполнена: {data.get('failMsg')}{data}")
                
                time.sleep(15)

            except Exception as e:
                logger.error(f"Ошибка опроса: {str(e)}")
                time.sleep(15)
        
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

        task_id = self._create_task(input_data)
        if not task_id:
            return {"success": False, "error": "Не удалось создать задачу"}

        result = self._poll_task(task_id)
        if not result:
            return {"success": False, "error": "Задача не выполнена"}
        
        suno_data = result.get('sunoData', [])
        if not suno_data:
            return {"success": False, "error": "Нет данных в результате"}
        
        first_result = suno_data[0] if isinstance(suno_data[0], dict) else {}
        audio_url = first_result.get('audioUrl', '')
        if not audio_url or not self._is_valid_url(audio_url):
            logger.error(f"Невалидный audioUrl: {audio_url}")
            return {"success": False, "error": "Невалидный URL в результате"}
        
        logger.info(f"✅ Музыка сгенерирована: {audio_url}")
        return {
            "success": True,
            "instrumental_url": audio_url,
            "prompt": prompt,
            "metadata": {
                "model": model,
                "style": input_data.get('style'),
                "duration": first_result.get('duration'),
                "title": first_result.get('title'),
                "tags": first_result.get('tags')
            }
        }