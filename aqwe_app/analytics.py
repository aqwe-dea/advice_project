import json
import os
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from pathlib import Path
from abc import abstractmethod
import logging
from datetime import datetime, timedelta
from collections import Counter

logger = logging.getLogger(__name__)

def log_interaction(user_id: str, endpoint: str, agent: str = None, metadata: dict = None):
    """Логирует взаимодействие пользователя с платформой в JSON-файл."""
    try:
        log_file = Path("user_interactions.json")
        
        # Загружаем существующие данные или создаём новые
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"total_visits": 0, "unique_users": [], "interactions": []}
        
        # Обновляем статистику
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "endpoint": endpoint,
            "agent": agent,
            "metadata": metadata or {}
        }
        
        data["total_visits"] += 1
        if user_id not in data["unique_users"]:
            data["unique_users"].append(user_id)
        data["interactions"].append(entry)
        
        # Ограничиваем размер файла (последние 1000 записей)
        if len(data["interactions"]) > 1000:
            data["interactions"] = data["interactions"][-1000:]
        
        # Сохраняем
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return True
    except Exception as e:
        logger.error(f"Ошибка логирования: {e}")
        return False

def get_stats(period_hours: int = 24) -> dict:
    """Возвращает простую статистику за последние N часов."""
    try:
        log_file = Path("user_interactions.json")
        if not log_file.exists():
            return {"error": "Нет данных"}
        
        with open(log_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        cutoff = datetime.utcnow() - timedelta(hours=period_hours)
        
        recent = [
            i for i in data.get("interactions", [])
            if datetime.fromisoformat(i["timestamp"]) > cutoff
        ]
        
        return {
            "total_visits": data.get("total_visits", 0),
            "unique_users": len(data.get("unique_users", [])),
            "recent_visits": len(recent),
            "top_endpoints": _count_by_field(recent, "endpoint"),
            "top_agents": _count_by_field(recent, "agent")
        }
    except Exception as e:
        return {"error": str(e)}

def _count_by_field(items: list, field: str) -> dict:
    """Вспомогательная функция для подсчёта значений по полю."""
    values = [i.get(field) for i in items if i.get(field)]
    return dict(Counter(values).most_common(10))