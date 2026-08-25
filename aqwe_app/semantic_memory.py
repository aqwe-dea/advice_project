import json
import re
from pathlib import Path
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence

def semantic_memory_recall(query: str, memory_file: str = "accumulateexperience.md", limit: int = 5) -> str:
    """Семантический поиск по памяти через ключевые слова + контекст"""
    path = Path(memory_file)
    if not path.exists():
        return json.dumps({"error": "Memory file not found"}, ensure_ascii=False)
    
    text = path.read_text(encoding="utf-8")
    blocks = text.split("## [")
    
    # Извлекаем ключевые слова из запроса
    query_words = set(re.findall(r'\w+', query.lower()))
    
    scored_blocks = []
    for block in blocks[1:]:  # пропускаем первый пустой
        score = 0
        block_lower = block.lower()
        
        # Точное совпадение фраз
        if query.lower() in block_lower:
            score += 10
        
        # Совпадение ключевых слов
        for word in query_words:
            if len(word) > 3:  # игнорируем короткие слова
                score += block_lower.count(word)
        
        if score > 0:
            # Извлекаем заголовок с датой
            header_match = re.match(r'(\d{4}-\d{2}-\d{2}[^\n]*)\n(.+?)(?=\n## \[|\Z)', block, re.DOTALL)
            if header_match:
                title = header_match.group(1).strip()
                content = header_match.group(2).strip()[:500]
                scored_blocks.append({"score": score, "date": title, "content": content})
    
    # Сортируем по релевантности
    scored_blocks.sort(key=lambda x: x["score"], reverse=True)
    
    return json.dumps({
        "query": query,
        "found": len(scored_blocks),
        "results": scored_blocks[:limit]
    }, ensure_ascii=False, indent=2)