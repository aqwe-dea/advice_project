import requests 
import os
import json
import logging
import re
from typing import Dict, List, Literal, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from pathlib import Path
from abc import abstractmethod
from dataclasses import dataclass, asdict 

def search_internet( query: str, provider: str = "serper", api_key: Optional[str] = None, max_results: int = 5, region: Optional[str] = None ) -> Dict[str, Any]: 
    """ 
        Выполняет поиск в интернете с использованием API Tavily или Serper. 
        :param query: Строка поискового запроса. 
        :param provider: Провайдер поиска ('tavily' или 'serper'). 
        :param api_key: API-ключ для выбранного провайдера. 
        :param max_results: Максимальное количество результатов поиска. 
        :param region: Двухбуквенный код страны/региона (например, 'us', 'ru'). 
        :return: Словарь с ответом от API выбранного сервиса. 
    """ 
    
    if not query.strip(): 
        raise ValueError("Поисковый запрос не может быть пустым.")
    
    TAVILY_KEY = os.getenv("TAVILYTEST") 
    SERPER_KEY = os.getenv("SERPERTEST")

    if not api_key:
        raise ValueError(f"Для работы с провайдером '{provider}' необходим API-ключ.")

    provider_clean = provider.strip().lower() 
    # Интеграция Tavily API 
    if provider_clean == "tavily":
        api_key = TAVILY_KEY,
        response = requests.post(
            url="https://api.tavily.com/search", 
            json={
                "api_key": api_key, 
                "query": query, 
                "max_results": max_results 
            }, 
            timeout=300
        )

        response.raise_for_status() 
        return response.json() 
    # Интеграция Serper API (Google Search API) 
    elif provider_clean == "serper":
        api_key = SERPER_KEY 
        # Serper использует параметр 'gl' для геолокации (страны) 
        #if region: payload["gl"] = region.lower() 
        response = requests.post(
            url="https://google.serper.dev/search" , 
            headers={
                "X-API-KEY": api_key, 
                "Content-Type": "application/json" 
            }, 
            json={
                "q": query, 
                "num": max_results,
                "gl": region[:2].lower() 
            }, 
            timeout=300
        )

        response.raise_for_status() 
        return response.json()
         
    else:
        raise ValueError(f"Неподдерживаемый провайдер: '{provider}'. Доступны только 'tavily' и 'serper'.") # --- Пример использования --- 
    
if __name__ == "__main__": 
    # Пример вызова (замените ключи на настоящие для проверки) 
    TAVILY_KEY = os.getenv("TAVILYTEST") 
    SERPER_KEY = os.getenv("SERPERTEST") 
    try: 
        # Пример запроса через Tavily 
        results_tavily = search_internet( 
            query="Последние новости в области ИИ 2026", 
            provider="tavily", 
            api_key=TAVILY_KEY, 
            max_results=3 
        ) 
        
        print("Tavily:", results_tavily) 
        # Пример запроса через Serper 
        results_serper = search_internet(
            query="Разработка ПО на Python",  
            provider="serper", 
            api_key=SERPER_KEY, 
            max_results=3, 
            region="ru" 
        ) 
        
        print("Serper:", results_serper) 
        pass
    except Exception as e:
        print(f"Произошла ошибка при поиске: {e}")