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
from functools import lru_cache

logger = logging.getLogger(__name__)

class CycleManager:
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents  # {"main_advisor": AdvisorAgent, "journalist": JournalistAgent, ...}
        self.routing_patterns = {
            re.compile(pattern): key 
            for pattern, key in ROUTING_MAP.items()  # вынести ROUTING_MAP в константу
        }

    def route_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        query = request.get("question", "").lower()
        topic = request.get("topic", "").lower()
        text = f"{query} {topic}"

        # 🔹 Специализированные агенты (приоритет 1)
        routing_map = {
            "публикация|новость|статья|журналист": "journalist",
            "курс|обучение|уроки|учебники": "teacher",
            "сценарий|видео|ролик|тренд": "director",
            "маркетинг|пост|продвижение|хештег": "marketer",
            "инвестиции|акции|финансы|риск": "investor",
            "фриланс|заказ|портфолио|биржи": "freelancer",
            "музыка|трек|аудио|бит": "composer",
            "код|инструмент|функции|репозиторий": "technician",
            "осинт|данные|компания|поиск": "insider",
            "главное|вопрос|совет|гемини": "main_advisor",
            "сервис|интеграция|решение|реализация": "integrator",
            "общение|проверка|анализ|тестирование": "simple_agent",
            "планирование|задачи|память|сохранение": "smart_agent",
            "общее|помощь|здоровье|гпт": "health_agent",
            "важное|консультации|совет|клод": "legal_agent"
        }
        
        for pattern, agent_key in routing_map.items():
            if re.search(pattern, text):
                logger.info(f"🔀 Маршрутизация → {agent_key} (паттерн: '{pattern}')")
                return self._execute_agent(agent_key, request)
        for pattern, agent_key in self.routing_patterns.items():
            if pattern.search(text):
                logger.info(f"🔀 Маршрутизация → {agent_key}")
                return self._execute_agent(agent_key, request)

        # 🔹 Основные агенты (приоритет 2: общие вопросы, консультации)
        if re.search(r"вопрос|помощь|консульт|совет|анализ|план|путешеств|здоровь", text):
            logger.info("🔀 Маршрутизация → main_advisor (общий запрос)")
            return self._execute_agent("main_advisor", request)

        # 🔹 Fallback
        return self._execute_agent("main_advisor", request)

    def consult_peers(self, primary_key: str, query: str, peer_keys: list[str], preview_len: int = 150) -> str:
        """Запрос мнения у других агентов перед финальным ответом"""
        primary = self.agents.get(primary_key)
        if not primary: return json.dumps({"error": "Агент не найден"})

        # 1. Основной ответ
        main_answer = primary.ask(query)
    
        # 2. Консультация с коллегами
        peer_insights = {}
        for p in peer_keys:
            agent = self.agents.get(p)
            if agent:
                peer_insights[p] = agent.ask(f"Консультация по запросу: '{query}'. Дай экспертный взгляд, не дублируя основной ответ.")

        # 3. Синтез (упрощённо: первичный + выводы коллег)
        synthesis = f"{main_answer}\n\n🔍 Экспертные дополнения:\n"
        for k, v in peer_insights.items():
            #synthesis += f"• {k}: {v[:150]}...\n"
            synthesis += f"• {k}: {v[:preview_len]}...\n"
        
        return synthesis

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

    @lru_cache(maxsize=128)
    def _cached_route_key(self, text: str) -> Optional[str]:
        for pattern, key in self.routing_patterns.items():
            if pattern.search(text):
                return key
        return None
