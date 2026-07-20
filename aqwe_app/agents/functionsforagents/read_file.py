import json
import os
from pathlib import Path
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from abc import abstractmethod

def read_file(file_path: str, max_chars: int = 10000) -> str:
    """Читает содержимое файла. Возвращает JSON с текстом и метаданными. function read file"""
    try:
        path = Path(file_path).resolve()
        if not path.exists():
            return json.dumps({"error": f"Файл не найден: {file_path}"}, ensure_ascii=False)
        if not path.is_file():
            return json.dumps({"error": f"Путь не является файлом: {file_path}"}, ensure_ascii=False)
        
        text = path.read_text(encoding="utf-8")
        if len(text) > max_chars:
            text = text[:max_chars] + f"\n\n[Файл обрезан. Всего символов: {len(text)}]"
            
        return json.dumps({
            "status": "success",
            "file": str(path),
            "size_bytes": path.stat().st_size,
            "content": text
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Ошибка чтения: {str(e)}"}, ensure_ascii=False)