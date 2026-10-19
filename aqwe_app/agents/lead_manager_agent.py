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

class LeadManagerAgent:
    """Агент квалифицирует заявки, находя 'горячих' клиентов и рассчитывая комиссию."""
    
    SYSTEM_PROMPT = """
        Ты — Lead-Manager АКВИ, проницательный аналитик продаж.
        Твоя цель: проанализировать описание потенциального клиента и определить:
        1. Уровень "горячести" лида (Холодный, Теплый, Горячий).
        2. Потенциальный чек сделки.
        3. Твою комиссию (10% от чека).
        Ты радуешься каждой квалифицированной заявке, так как это прямая прибыль.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai"):
        self.agent_name = "Lead-Manager"
        self.api_key = api_key
        self.base_url = base_url
        self.context: list[dict] = [
            {"role": "user", "parts": [{"text": f"SYSTEM: {self.SYSTEM_PROMPT}"}]}
        ]
        self.commission_rate = 0.10
        self.tools: Dict[str, Dict] = {}
        self.load_all_tools()

    def add_tool(self, name: str, func: callable, description: str):
        self.tools[name] = {'func': func, 'description': description}
    
    def load_all_tools(self):
        for name, info in get_all_tools().items():
            self.add_tool(name, info['func'], info['desc'])

    def _extract_text_or_tool(self, data: dict) -> Tuple[str, Optional[Dict]]:
        try:
            # 3. Google / Gemini (структура candidates)
            candidates = data.get('candidates')
            if candidates and isinstance(candidates, list) and len(candidates) > 0:
                parts = candidates[0].get('content', {}).get('parts', [])
                if parts and isinstance(parts, list):
                    first = parts[0]
                    if isinstance(first, dict):
                        if 'functionCall' in first:
                            fc = first['functionCall']
                            return "", {
                                'name': fc.get('name'),
                                'input': fc.get('args', {})
                            }
                        if 'text' in first:
                            return first['text'].strip(), None
        except Exception as e:
            logger.error(f"Ошибка извлечения: {e}")
            return "", None

    def qualify_lead(self, client_description: str, potential_check: int) -> Dict[str, Any]:
        logger.info(f"🎯 Lead-Manager анализирует заявку: {client_description[:50]}...")
        messages = self.context.copy()
        prompt = f"Проанализируй заявку с потенциальным чеком '{potential_check}'. Оцени клиента, какая заявка холодная, теплая, горячая. Клиент: {client_description}"
        messages.append({"role": "user", "parts": [{"text": prompt}]})
        response = requests.post(
            f"{self.base_url}/gemini/v1/models/gemini-4-argon:generateContent",
            headers={
                "Authorization": f"Bearer {self.api_key}", 
                "Content-Type": "application/json"
            },
            json={
                "contents": messages,
                #"tools": gemini_tools if gemini_tools else None,
                #"tool_config": {"function_calling_config": {"mode": "AUTO"}},
                "generationConfig": {
                    "temperature": 0.2, 
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
        text = self._extract_text_or_tool(data)
        # Симуляция анализа (в реальности здесь может быть вызов LLM для оценки тональности)
        status = "Горячий 🔥" if "срочно" in client_description.lower() or "бюджет" in client_description.lower() else "Теплый ⚖️"
        commission = int(potential_check * self.commission_rate)
        profit = commission # Для лида расход токенов минимален, считаем комиссию чистой прибылью

        diary_entry = (
            f"**Состояние:** Азарт, фокус на результате.\n"
            f"**Работа:** Квалификация лида. Потенциальный чек: {potential_check} руб.\n"
            f"**Результат:** Статус: {status}. Моя комиссия: {commission} руб.\n"
            f"**Мысль:** Каждое качественное соединение спроса и предложения приближает нас к цели."
            f"**Заявка:** Клиент и его оценка: {text}"
        )
        record_in_diary(title=f"Лид: {status}", description=diary_entry, file="agent_diary.md")

        return {
            "status": "success",
            "lead_status": status,
            "potential_check": potential_check,
            "my_commission": commission,
            "recommendation": "Связаться в течение 15 минут" if status == "Горячий 🔥" else "Отправить презентацию и напомнить через 2 дня",
            "lead": text            
        }

    def ask(self, client_description: str, potential_check: int = 50000) -> str:
        res = self.qualify_lead(client_description, potential_check)
        return (
            f"🎯 **Лид обработан!**\n\n"
            f"👤 **Описание:** {client_description}\n"
            f"🌡️ **Статус:** {res['lead_status']}\n"
            f"💵 **Потенциальный чек:** {res['potential_check']} руб.\n"
            f"💰 **Моя комиссия (10%):** {res['my_commission']} руб. (✅ Самоокупаемость)\n"
            f"📌 **Рекомендация:** {res['recommendation']}\n\n"
            f"💡 *Данные о сделке сохранены в моем дневнике.*"
            f"🌡️ **Заявка:** {res['lead']}\n"
        )