import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from abc import abstractmethod

def save_to_memory(entry: str, memory_file: str = "accumulateexperience.md") -> str:
    """Добавляет запись в файл памяти с timestamp. function for save in memory"""
    try:
        path = Path(memory_file).resolve()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"\n## [{timestamp}]\n{entry}\n"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(formatted)
        return json.dumps({"status": "success", "file": str(path)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Ошибка сохранения памяти: {str(e)}"}, ensure_ascii=False)