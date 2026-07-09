from __future__ import annotations

import os
import json
import logging
import re
import requests
from typing import List, Optional, Literal, Dict, Any

logger = logging.getLogger(__name__)

Provider = Literal["tavily", "serper"]

class SearchResult:
    """
    web_search.py — универсальный инструмент веб-поиска для Python-агентов.

    Поддерживает несколько провайдеров:
    - "tavily"  : Tavily API (нужен TAVILY_API_KEY)
    - "serper"  : Serper.dev / Google (нужен SERPER_API_KEY)
    """
    title: str
    url: str
    snippet: str

    def to_dict(self) -> dict:
        return Dict(self)


# ---------- Провайдеры ----------
def _search_tavily(query: str, max_results: int) -> List[SearchResult]:
    api_key = os.getenv("TAVILYTEST")
    if not api_key:
        raise RuntimeError("TAVILYTEST не задан в переменных окружения")

    resp = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
        },
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    return [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("url", ""),
            snippet=item.get("content", ""),
        )
        for item in data.get("results", [])
    ]


def _search_serper(query: str, max_results: int, region: str) -> List[SearchResult]:
    api_key = os.getenv("SERPERTEST")
    if not api_key:
        raise RuntimeError("SERPERTEST не задан в переменных окружения")

    resp = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        json={"q": query, "num": max_results, "gl": region[:2].lower()},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    return [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("link", ""),
            snippet=item.get("snippet", ""),
        )
        for item in data.get("organic", [])[:max_results]
    ]


# ---------- Публичный API инструмента ----------

def web_search(
    query: str,
    max_results: int = 5,
    provider: Provider = "tavily",
    region: str = "ru-ru",
) -> str:
    """
    Ищет информацию в интернете и возвращает результаты в виде JSON-строки.

    Args:
        query: Поисковый запрос (обязателен, непустой).
        max_results: Сколько результатов вернуть (1..20).
        provider: "tavily" | "serper".
        region: Регион поиска (например, "ru-ru", "us-en", "wt-wt").

    Returns:
        JSON-строка вида:
        {"query": "...", "provider": "...", "results": [{"title","url","snippet"}, ...]}

        При ошибке возвращает JSON с полем "error" — это удобно для агента,
        который парсит ответ инструмента.
    """
    if not query or not query.strip():
        return json.dumps({"error": "Пустой запрос"}, ensure_ascii=False)

    max_results = max(1, min(int(max_results), 20))

    try:
        if provider == "tavily":
            results = _search_tavily(query, max_results)
        elif provider == "serper":
            results = _search_serper(query, max_results, region)
        else:
            return json.dumps({"error": f"Неизвестный провайдер: {provider}"}, ensure_ascii=False)

        return json.dumps(
            {
                "query": query,
                "provider": provider,
                "results": [r.to_dict() for r in results],
            },
            ensure_ascii=False,
        )
    except Exception as e:
        logger.exception("Ошибка поиска")
        return json.dumps({"error": str(e), "query": query}, ensure_ascii=False)


if __name__ == "__main__":
    print(web_search("новости искусственного интеллекта", max_results=3, region="ru-ru"))