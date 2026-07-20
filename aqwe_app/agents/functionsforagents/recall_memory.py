import json
from pathlib import Path
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from abc import abstractmethod

def recall_memory(query: str, memory_file: str = "accumulateexperience.md", limit: int = 3) -> str:
    """Ищет записи в памяти по ключевым словам. function for call memory"""
    try:
        path = Path(memory_file).resolve()
        if not path.exists():
            return json.dumps({"status": "empty", "message": "Файл памяти не найден"}, ensure_ascii=False)
        
        text = path.read_text(encoding="utf-8")
        lines = text.split("\n")
        matches = []
        for i, line in enumerate(lines):
            if query.lower() in line.lower():
                # Берем блок (заголовок + содержание)
                start = max(0, i-1)
                end = min(len(lines), i+5)
                matches.append("\n".join(lines[start:end]))
            if len(matches) >= limit:
                break
                
        return json.dumps({
            "status": "success",
            "query": query,
            "matches": matches if matches else ["Совпадений не найдено."]
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Ошибка поиска в памяти: {str(e)}"}, ensure_ascii=False)