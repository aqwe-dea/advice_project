import json
import os
import logging
#import fcntl
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from pathlib import Path
from abc import abstractmethod
from datetime import datetime, timezone, timedelta
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "endpoint": endpoint,
            "agent": agent,
            "metadata": metadata or {}
        }
        
        data["total_visits"] += 1
        if user_id not in data["unique_users"]:
            data["unique_users"].append(user_id)
        data["interactions"].append(entry)

        MAX_INTERACTIONS = 1000
        if len(data["interactions"]) > MAX_INTERACTIONS:
            data["interactions"] = data["interactions"][-MAX_INTERACTIONS:]
        # Ограничиваем размер файла (последние 1000 записей)
        
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

def _load_json(path: Path) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"total_visits": 0, "unique_users": [], "interactions": []}

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

#def _atomic_write(path: Path, data: dict):
#    with open(path, "w", encoding="utf-8") as f:
#        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
#        json.dump(data, f, ensure_ascii=False, indent=2)
#        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def _count_by_field(items: list, field: str) -> dict:
    """Вспомогательная функция для подсчёта значений по полю."""
    values = [i.get(field) for i in items if i.get(field)]
    return dict(Counter(values).most_common(10))

def track_journey(user_id: str, step: str, metadata: dict = None):
    log_file = Path("user_interactions.json")
        
    # Загружаем существующие данные или создаём новые
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            #data = json.load(f)
            data = _load_json(log_file) # твоя функция загрузки
            if user_id not in data:
                data[user_id] = {"journey": [], "last_active": None}
    
            data[user_id]["journey"].append({
                "step": step,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "meta": metadata or {}
            })
            
            data[user_id]["last_active"] = datetime.now(timezone.utc).isoformat()
    
            #_save_json(data, log_file)
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return True