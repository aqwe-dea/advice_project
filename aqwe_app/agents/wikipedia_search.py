from __future__ import annotations
import os
import json
import logging
import re
import requests
from typing import Dict, List, Literal, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from pathlib import Path
from abc import abstractmethod
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class FindedPage:
    """
    wikipedia_search.py — инструмент для поиска в Wikipedia.

    Возвращает заголовок, краткое описание и ссылку на статью.
    """
    title: str
    snippet: str
    url: str

    def to_dict(self) -> dict:
        return Dict(self)

def search_by_wikipedia(query: str, lang: str = "ru", max_results: int = 3) -> str:
    """
    Ищет статьи в Wikipedia и возвращает результаты.
    
    Args:
        query: Поисковый запрос (обязателен)
        lang: Язык Wikipedia ('ru', 'en', 'de' и т.д.)
        max_results: Максимальное количество результатов (1-10)
    
    Returns:
        JSON-строка со списком статей (заголовок, описание, url).
        При ошибке возвращает JSON с полем "error".
    """
    
    if not query or not query.strip():
        return json.dumps({"error": "Пустой запрос"}, ensure_ascii=False)
    
    max_results = max(1, min(int(max_results), 10))
    
    # Wikipedia API endpoint
    endpoint = f"https://{lang}.wikipedia.org/w/api.php"
    
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": max_results,
        "format": "json"
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("query", {}).get("search", []):
            # Извлекаем краткое описание (snippet) без HTML-тегов
            snippet = item.get("snippet", "")
            # Удаляем HTML-теги из сниппета
            clean_snippet = BeautifulSoup(snippet, 'html.parser').get_text()
            
            results.append({
                "title": item.get("title", ""),
                "snippet": clean_snippet,
                "url": f"https://{lang}.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}",
                "wordcount": item.get("wordcount", 0),
            })
        
        return json.dumps({
            "query": query,
            "language": lang,
            "results": results,
            "count": len(results)
        }, ensure_ascii=False)
        
    except requests.exceptions.Timeout:
        return json.dumps({"error": "Таймаут при запросе к Wikipedia"}, ensure_ascii=False)
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Ошибка запроса к Wikipedia: {str(e)}"}, ensure_ascii=False)
    except Exception as e:
        logger.exception(f"Ошибка поиска в Wikipedia")
        return json.dumps({"error": f"Ошибка: {str(e)}"}, ensure_ascii=False)


if __name__ == "__main__":
    print(search_by_wikipedia("искусственный интеллект", lang="ru", max_results=3))