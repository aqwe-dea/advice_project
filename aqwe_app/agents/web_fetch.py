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

class FetchResult:
    """
    web_fetch.py — инструмент для загрузки и парсинга веб-страниц.

    Извлекает основной контент, очищает от рекламы/навигации,
    возвращает заголовок, текст и метаданные.
    """
    title: str
    text: str
    description: str
    url: str

    def to_dict(self) -> dict:
        return Dict(self)

def web_fetch(url: str, max_length: int = 5000) -> str:
    """
    Загружает веб-страницу и извлекает основной текст.
    
    Args:
        url: Адрес страницы (обязателен, должен начинаться с http:// или https://)
        max_length: Максимальная длина возвращаемого текста (по умолчанию 5000)
    
    Returns:
        JSON-строка с заголовком, текстом и метаданными.
        При ошибке возвращает JSON с полем "error".
    """
    
    if not url or not url.strip():
        return json.dumps({"error": "Пустой URL"}, ensure_ascii=False)
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Удаляем ненужные элементы
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript']):
            element.decompose()
        
        # Извлекаем заголовок
        title = soup.title.string if soup.title else 'Без заголовка'
        
        # Извлекаем основной текст
        text = soup.get_text(separator='\n', strip=True)
        
        # Ограничиваем длину
        if len(text) > max_length:
            text = text[:max_length] + '... [текст обрезан]'
        
        # Извлекаем мета-описание
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ''
        
        result = {
            "url": url,
            "title": title,
            "description": description,
            "text": text,
            "word_count": len(text.split()),
        }
        
        return json.dumps(result, ensure_ascii=False)
        
    except requests.exceptions.Timeout:
        return json.dumps({"error": f"Таймаут при загрузке {url}"}, ensure_ascii=False)
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Ошибка загрузки {url}: {str(e)}"}, ensure_ascii=False)
    except Exception as e:
        logger.exception(f"Ошибка парсинга {url}")
        return json.dumps({"error": f"Ошибка парсинга: {str(e)}"}, ensure_ascii=False)


if __name__ == "__main__":
    print(web_fetch("https://ru.wikipedia.org/wiki/Искусственный_интеллект"))