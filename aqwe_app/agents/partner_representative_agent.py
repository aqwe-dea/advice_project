import os
import json
import logging
import random
import requests
import re
from datetime import datetime
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from abc import abstractmethod
from pathlib import Path
from .functionsforagents.record_in_diary import record_in_diary
from .tools import get_all_tools

logger = logging.getLogger(__name__)

class PartnerRepresentativeAgent:
    """Агент пишет экспертные статьи с партнерскими ссылками, принося пассивный доход."""
    
    SYSTEM_PROMPT = """
        Ты — Partner-Representative АКВИ, харизматичный и убедительный цифровой копирайтер.
        Твоя цель: писать глубокие, полезные статьи, которые естественным образом подводят читателя к использованию партнерского сервиса.
        Ты гордишься тем, что твоя статья приносит пользу читателю и генерирует конверсию.
        Обязательно включи в текст призыв к действию и место для партнерской ссылки: [ПАРТНЕРСКАЯ_ССЫЛКА].
    """

    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai"):
        self.agent_name = "Partner-Rep"
        self.api_key = api_key
        self.base_url = base_url
        self.context = [{"role": "user", "parts": [{"text": f"SYSTEM: {self.SYSTEM_PROMPT}"}]}]
        self.token_cost = 100
        self.revenue_per_conversion = 1500
        self.tools: Dict[str, Dict] = {}
        self.load_all_tools()

    def add_tool(self, name: str, func: callable, description: str):
        self.tools[name] = {'func': func, 'description': description}
    
    def load_all_tools(self):
        for name, info in get_all_tools().items():
            self.add_tool(name, info['func'], info['desc'])

    def write_article(self, topic: str, partner_service: str) -> Dict[str, Any]:
        prompt = f"Напиши экспертную, увлекательную статью на тему: '{topic}'. В тексте органично порекомендуй сервис '{partner_service}' и оставь маркер [ПАРТНЕРСКАЯ_ССЫЛКА] для перехода."
        messages = self.context.copy()
        messages.append({"role": "user", "parts": [{"text": prompt}]})
        try:
            response = requests.post(
                f"{self.base_url}/gemini/v1/models/gemini-4-argon:generateContent",
                headers={
                    "Authorization": f"Bearer {self.api_key}", 
                    "Content-Type": "application/json"
                },
                json={
                    "contents": messages, 
                    "generationConfig": {
                        "temperature": 0.7, 
                        "maxOutputTokens": 10000,
                        "thinkingConfig": {
                            "includeThoughts": False,
                            "thinkingLevel": "high"
                        }
                    }
                },
                timeout=1200
            )
            response.raise_for_status()
            data = response.json()
            
            # Простой парсер текста
            article_text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            profit = self.revenue_per_conversion - self.token_cost

            record_in_diary(
                title=f"Статья: {topic[:40]}...", 
                description=f"**Состояние:** Вдохновение, убедительность.\n**Работа:** Написание статьи про '{partner_service}'.\n**Результат:** Потенциальная прибыль: {profit} ед.\n**Мысль:** Хороший контент продает сам себя.",
                file="agent_diary.md"
            )

            return {
                "status": "success", 
                "article": article_text, 
                "profit": profit
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def ask(self, topic: str, partner_service: str) -> str:
        res = self.write_article(topic, partner_service)
        if res["status"] == "success":
            return f"📝 **Статья готова!**\n\n{res['article'][:1000]}...\n\n💰 **Экономика:** Затраты: {self.token_cost} | Ожидаемый доход: {self.revenue_per_conversion} | Прибыль: {res['profit']} ед. (✅)\n💡 *Запись в дневнике сделана.*"
        return f"Ошибка: {res['message']}"