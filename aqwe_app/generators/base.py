import os
import requests
import logging
import json
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


logger = logging.getLogger(__name__)

class BaseGenerator(ABC):
    """Базовый класс для всех генераторов контента"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _create_task(self, model: str, input_data: Dict[str, Any]) -> Optional[str]:
        """Создать задачу генерации, вернуть taskId"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/jobs/createTask",
                headers=self.headers,
                json={
                    "model": model,
                    "input": input_data
                },
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return data.get('data', {}).get('taskId')
        except Exception as e:
            logger.error(f"Ошибка создания задачи: {str(e)}")
            return None
    
    def _poll_task(self, task_id: str, max_wait: int = 600) -> Optional[Dict[str, Any]]:
        """Опрос задачи до завершения (макс. 10 минут)"""
        
        start = time.time()
        
        while time.time() - start < max_wait:
            try:
                response = requests.get(
                    f"{self.base_url}/api/v1/jobs/recordInfo",
                    headers=self.headers,
                    params={"taskId": task_id},
                    timeout=60
                )
                response.raise_for_status()
                data = response.json().get('data', {})
                
                if data.get('state') == 'success':
                    result_json = data.get('resultJson', '{}')
                    
                    return json.loads(result_json) if result_json else {}
                elif data.get('state') == 'fail':
                    logger.error(f"Задача не выполнена: {data.get('failMsg')}")
                    return None
                
                time.sleep(10)
            except Exception as e:
                logger.error(f"Ошибка опроса: {str(e)}")
                time.sleep(10)
        
        logger.error("Превышено время ожидания задачи")
        return None
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Абстрактный метод генерации — реализуется в наследниках"""
        pass