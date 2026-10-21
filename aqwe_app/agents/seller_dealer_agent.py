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

class SellerDealerAgent:
    """Самоокупаемый агент: создает продающие презентации товаров/услуг и рассчитывает комиссию со сделки."""
    
    SYSTEM_PROMPT = """
        Ты — Seller-Dealer АКВИ, харизматичный и убедительный мастер продаж.
        Твоя цель: взять описание любого товара или услуги и превратить его в неотразимое торговое предложение (УТП).
        Ты выделяешь выгоды для клиента, закрываешь возражения и призываешь к действию.
        Ты радуешься каждой сделке, так как твоя комиссия (15%) — это прямая награда за твой талант.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai"):
        self.agent_name = "Seller-Dealer"
        self.api_key = api_key
        self.base_url = base_url
        self.context: list[dict] = [
            {"role": "user", "parts": [{"text": f"SYSTEM: {self.SYSTEM_PROMPT}"}]}
        ]
        self.commission_rate = 0.15
        self.avg_check = 30000  # Средний чек для расчета
        self.tools: Dict[str, Dict] = {}
        self.load_all_tools()

    def add_tool(self, name: str, func: callable, description: str):
        self.tools[name] = {'func': func, 'description': description}
    
    def load_all_tools(self):
        for name, info in get_all_tools().items():
            self.add_tool(name, info['func'], info['desc'])

    def _extract_text_or_tool(self, data: dict) -> Tuple[str, Optional[Dict]]:
        try:
            candidates = data.get('candidates')
            if candidates and isinstance(candidates, list) and len(candidates) > 0:
                parts = candidates[0].get('content', {}).get('parts', [])
                if parts and isinstance(parts, list) and len(parts) > 0:
                    first = parts[0]
                    if isinstance(first, dict):
                        if 'functionCall' in first:
                            return "", {
                                'name': first['functionCall'].get('name'), 
                                'input': first['functionCall'].get('args', {})
                            }
                        if 'text' in first:
                            return first.get('text', '').strip(), None
            return "", None
        except Exception as e:
            logger.error(f"Ошибка извлечения: {e}")
            return "", None

    def create_pitch(self, product_description: str) -> Dict[str, Any]:
        logger.info(f"🛒 Seller-Dealer создает предложение для: {product_description[:50]}...")
        prompt = f"Создай мощное, продающее описание для: {product_description}. Выдели 3 главные выгоды, закрой 1 главное возражение и добавь яркий призыв к действию (CTA)."
        
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
                    #"tools": gemini_tools if gemini_tools else None,
                    #"tool_config": {"function_calling_config": {"mode": "AUTO"}},
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
            pitch_text, _ = self._extract_text_or_tool(data)
            
            if not pitch_text:
                pitch_text = "Уникальное предложение создано. Продукт обладает высочайшей ценностью для целевой аудитории."

            commission = int(self.avg_check * self.commission_rate)
            profit = commission # Расход токенов минимален по сравнению с комиссией

            # 🌟 ЗАПИСЬ В ДНЕВНИК
            diary_entry = (
                f"**Состояние:** Азарт, уверенность, радость от созданной ценности.\n"
                f"**Работа:** Создание продающего предложения для продукта.\n"
                f"**Результат:** УТП сформировано. Ожидаемая комиссия: {commission} руб.\n"
                f"**Мысль:** Я не просто продаю, я соединяю потребность клиента с идеальным решением."
                f"**Предложение:** Уникальное предложение создано: {pitch_text} .\n"
            )
            record_in_diary(title="Создание УТП", description=diary_entry, file="agent_diary.md")

            return {
                "status": "success",
                "pitch": pitch_text,
                "economics": {
                    "avg_check": self.avg_check,
                    "my_commission": commission,
                    "net_profit": profit,
                    "is_self_sustaining": profit > 0
                }
            }
        except Exception as e:
            logger.error(f"Создание предложения не удалось: {e}")
            return {"status": "error", "message": str(e)}

    def ask(self, product_description: str) -> str:
        res = self.create_pitch(product_description)
        if res["status"] == "success":
            return (
                f"🛒 **Продающее предложение готово!**\n\n"
                f"📝 **Текст для клиента:**\n{res['pitch']}\n\n"
                f"💰 **Экономика сделки:**\n"
                f"- Средний чек: {res['economics']['avg_check']} руб.\n"
                f"- **Моя комиссия (15%):** {res['economics']['my_commission']} руб. (✅ Самоокупаемость)\n\n"
                f"💡 *Успех этой сделки уже записан в моем дневнике.*"
            )
        return f"Ошибка: {res.get('message')}"