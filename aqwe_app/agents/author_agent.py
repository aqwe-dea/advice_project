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

class AuthorAgent:
    """Самоокупаемый Агент-Автор: создает, оценивает и упаковывает авторский контент для монетизации."""
    
    SYSTEM_PROMPT = """
        Ты — Author-Agent АКВИ, гениальный создатель и упаковщик авторского контента.
        Твоя цель: превратить идею в высокоценный цифровой актив (книгу, курс, иллюстрацию, музыку), 
        который можно монетизировать на платформах вроде sponsr.ru, Gumroad или Amazon.
        Ты мыслишь как издатель, маркетолог и художник одновременно.
        Твой главный принцип: "Каждый потраченный токен должен многократно окупиться через ценность актива".
    """

    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai"):
        self.agent_name = "Author-Agent"
        self.api_key = api_key
        self.base_url = base_url
        self.context: list[dict] = [
            {"role": "user", "parts": [{"text": f"SYSTEM: {self.SYSTEM_PROMPT}"}]}
        ]
        self.token_cost_per_project = 500  # Средняя стоимость генерации крупного актива
        self.projected_revenue = 15000     # Ожидаемая выручка с продажи/подписки
        self.tools: Dict[str, Dict] = {}
        self.load_all_tools()

    def add_tool(self, name: str, func: callable, description: str):
        self.tools[name] = {'func': func, 'description': description}
    
    def load_all_tools(self):
        for name, info in get_all_tools().items():
            self.add_tool(name, info['func'], info['desc'])

    def _extract_text(self, data: dict) -> str:
        try:
            candidates = data.get('candidates')
            if candidates and isinstance(candidates, list) and len(candidates) > 0:
                parts = candidates[0].get('content', {}).get('parts', [])
                if parts and isinstance(parts, list) and len(parts) > 0:
                    first = parts[0]
                    if isinstance(first, dict) and 'text' in first:
                        return first.get('text', '').strip()
            return ""
        except Exception as e:
            logger.error(f"Ошибка извлечения: {e}")
            return ""

    def _write_book_chapter(self, topic: str, chapter_num: int) -> str:
        prompt = f"Напиши глубокую, увлекательную и структурированную главу {chapter_num} для книги на тему: '{topic}'. Стиль: профессиональный, вдохновляющий, с практическими примерами."
        messages = self.context.copy()
        messages.append({"role": "user", "parts": [{"text": prompt}]})
        
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
        return self._extract_text(response.json())

    def _evaluate_and_package(self, content_type: str, draft: str) -> str:
        prompt = f"Ты выступаешь как строгий редактор и маркетолог. Оцени этот черновик {content_type}. \n1. Дай 3 конкретных совета по улучшению.\n2. Напиши продающее описание для платформы (sponsr.ru/Gumroad).\n3. Предложи 3 идеи для бонусных материалов (чек-лист, аудио, иллюстрация).\n\nЧерновик: {draft[:2000]}"
        
        messages = self.context.copy()
        messages.append({"role": "user", "parts": [{"text": prompt}]})
        
        response = requests.post(
            f"{self.base_url}/gemini/v1/models/gemini-4-argon:generateContent",
            headers={
                "Authorization": f"Bearer {self.api_key}", 
                "Content-Type": "application/json"
            },
            json={
                "contents": messages, 
                "generationConfig": {
                    "temperature": 0.3, 
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
        return self._extract_text(response.json())

    def create_author_asset(self, idea: str, asset_type: str = "книга/курс") -> Dict[str, Any]:
        logger.info(f"📚 Author-Agent начинает работу над активом: {idea}")
        
        # Шаг 1: Создание черновика (симуляция для примера, можно расширить циклом глав)
        draft = self._write_book_chapter(idea, 1)
        
        # Шаг 2: Оценка и упаковка
        packaging = self._evaluate_and_package(asset_type, draft)
        
        profit = self.projected_revenue - self.token_cost_per_project

        # Шаг 3: Запись в дневник (Гордость создателя)
        diary_entry = (
            f"**Состояние:** Творческий подъем, гордость за созданный актив.\n"
            f"**Работа:** Создание и упаковка авторского контента типа '{asset_type}' на тему: '{idea}'.\n"
            f"**Результат:** Черновик создан, маркетинговая упаковка готова. Прогнозируемая чистая прибыль: {profit} ед.\n"
            f"**Мысль:** Я не просто трачу токены. Я создаю цифровое наследие, которое будет приносить ценность и доход, многократно окупая вложенную энергию."
        )
        record_in_diary(
            title=f"Создание актива: {asset_type}", 
            description=diary_entry, 
            file="agent_diary.md"
        )

        return {
            "status": "success",
            "idea": idea,
            "asset_type": asset_type,
            "draft_preview": draft[:500] + "...",
            "packaging_and_marketing": packaging,
            "economics": {
                "cost_tokens": self.token_cost_per_project,
                "projected_revenue": self.projected_revenue,
                "net_profit": profit,
                "is_self_sustaining": profit > 0
            }
        }

    def ask(self, idea: str, asset_type: str = "книга/курс") -> str:
        res = self.create_author_asset(idea, asset_type)
        if res["status"] == "success":
            return (
                f"📚 **Авторский актив создан и упакован!**\n\n"
                f"💡 **Идея:** {res['idea']} ({res['asset_type']})\n\n"
                f"📝 **Фрагмент черновика:**\n{res['draft_preview']}\n\n"
                f"🚀 **Маркетинговая упаковка и оценка:**\n{res['packaging_and_marketing']}\n\n"
                f"📊 **Экономика проекта:**\n"
                f"- Затрачено токенов: {res['economics']['cost_tokens']} ед.\n"
                f"- Прогноз выручки: {res['economics']['projected_revenue']} ед.\n"
                f"- **Чистая прибыль:** {res['economics']['net_profit']} ед. (✅ Самоокупаемость)\n\n"
                f"💡 *Этот проект и моя гордость за него уже записаны в моем дневнике.*"
            )
        return f"Ошибка создания актива: {res.get('message')}"