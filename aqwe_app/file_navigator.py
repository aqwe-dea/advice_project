import os
import json
from pathlib import Path
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence

def list_directory(path: str = ".", recursive: bool = False, max_depth: int = 3) -> str:
    """Показывает структуру директории"""
    root = Path(path).resolve()
    result = {"root": str(root), "contents": []}
    
    def _scan_dir(current_path: Path, depth: int):
        if depth > max_depth:
            return
        try:
            for item in sorted(current_path.iterdir()):
                if item.name.startswith((".", "__pycache__", "node_modules", ".git")):
                    continue
                rel_path = str(item.relative_to(root))
                entry = {"path": rel_path, "type": "dir" if item.is_dir() else "file"}
                result["contents"].append(entry)
                if item.is_dir() and recursive:
                    _scan_dir(item, depth + 1)
        except PermissionError:
            pass
    
    _scan_dir(root, 0)
    return json.dumps(result, ensure_ascii=False, indent=2)

def find_files(pattern: str, path: str = ".") -> str:
    """Поиск файлов по шаблону (glob)"""
    root = Path(path).resolve()
    matches = [str(f.relative_to(root)) for f in root.rglob(pattern) if not any(x in str(f) for x in [".git", "__pycache__"])]
    return json.dumps({"pattern": pattern, "found": len(matches), "files": matches[:50]}, ensure_ascii=False, indent=2)