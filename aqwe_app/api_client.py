import os
import requests
import json
import time
import logging
import re
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from datetime import datetime
from uuid import UUID
from abc import abstractmethod
from pathlib import Path

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, api_key: str, base_url: str = "", max_retries: int = 3, timeout: int = 300):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AQWE-Platform/1.0"
        })

    def request(self, method: str, endpoint: str, json: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        for attempt in range(self.max_retries):
            try:
                resp = self.session.request(method, url, json=json, timeout=self.timeout)
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.Timeout:
                logger.warning(f"Таймаут {method} {url} (попытка {attempt+1}/{self.max_retries})")
                time.sleep(2 ** attempt)  # Экспоненциальная задержка
            except requests.exceptions.RequestException as e:
                logger.error(f"Запрос не удался: {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        return {}