from pathlib import Path
import logging
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from abc import abstractmethod

logger = logging.getLogger(__name__)

def load_md_files(file_list: list[str], base_dir: str = ".") -> str:
    """Загружает содержимое .md файлов и возвращает объединённый текст."""
    content = []
    for f in file_list:
        try:
            path = Path(base_dir) / f
            text = path.read_text(encoding='utf-8')
            content.append(f"\n## 📄 {f}\n{text}\n")
        except FileNotFoundError:
            logger.warning(f"Файл не найден: {f}")
            content.append(f"\n## 📄 {f}\n[Файл не загружен]\n")
        except Exception as e:
            logger.error(f"Ошибка загрузки {f}: {e}")
            content.append(f"\n## 📄 {f}\n[Ошибка: {str(e)}]\n")
    return "\n".join(content)