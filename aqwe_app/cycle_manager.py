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

class CycleManager:
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents  # {"main_advisor": AdvisorAgent, "journalist": JournalistAgent, ...}

    def route_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        query = request.get("question", "").lower()
        topic = request.get("topic", "").lower()
        text = f"{query} {topic}"

        # 🔹 Специализированные агенты (приоритет 1)
        routing_map = {
            "публик|новост|стать|журналист": "journalist",
            "курс|обучен|уро|учеб": "teacher",
            "сценар|видео|ролик|тренд": "director",
            "маркет|пост|продвижен|хештег": "marketer",
            "инвест|акци|финанс|риск": "investor",
            "фриланс|заказ|портфолио|бирж": "freelancer",
            "музык|трек|аудио|бит": "composer",
            "код|инструмент|функци|репозиторий": "technician",
            "осинт|данны|компани|поиск": "insider"
        }

        
        for pattern, agent_key in routing_map.items():
            if re.search(pattern, text):
                logger.info(f"🔀 Маршрутизация → {agent_key} (паттерн: '{pattern}')")
                return self._execute_agent(agent_key, request)

        # 🔹 Основные агенты (приоритет 2: общие вопросы, консультации)
        if re.search(r"вопрос|помощь|консульт|совет|анализ|план|путешеств|здоровь", text):
            logger.info("🔀 Маршрутизация → main_advisor (общий запрос)")
            return self._execute_agent("main_advisor", request)

        # 🔹 Fallback
        return self._execute_agent("main_advisor", request)

    def _execute_agent(self, agent_key: str, request: Dict) -> Dict:
        agent = self.agents.get(agent_key)
        if not agent:
            return {"error": f"Агент '{agent_key}' не найден в реестре"}
        try:
            result = agent.ask(request.get("question", ""))
            return {"agent": agent_key, "result": result, "status": "success"}
        except Exception as e:
            logger.error(f"Ошибка агента {agent_key}: {e}")
            return {"error": str(e), "status": "failed"}