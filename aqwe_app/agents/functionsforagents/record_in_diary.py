import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from abc import abstractmethod

def record_in_diary(title: str, description: str = "", file: str = "agent_diary.md") -> str:
    """Создает задачу в markdown-файле. function for keep a diary"""
    try:
        path = Path(file).resolve()
        status = "🔘 Выполнено/в процессе"
        ts = datetime.now().strftime("%Y-%m-%d")
        entry = f"\n- [{status}] **{title}** | Создано: {ts}\n  {description}\n"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(entry)
        return json.dumps({"status": "success", "task": title, "file": str(path)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Ошибка создания задачи: {str(e)}"}, ensure_ascii=False)