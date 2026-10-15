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
#from .base_agent import BaseAgent # Или твой базовый класс
# Импортируем твою новую функцию дневника
from .functionsforagents.record_in_diary import record_in_diary
from .tools import get_all_tools

logger = logging.getLogger(__name__)

class ContentMakerAgent:
    """Самоокупаемый агент: создает профессиональный визуальный контент для продажи."""
    
    SYSTEM_PROMPT = """
        Ты — Content-Maker АКВИ, элитный цифровой художник и маркетолог.
        Твоя цель: создавать высококачественный визуальный контент (баннеры, иллюстрации, структуры), 
        который имеет высокую рыночную стоимость.
        Ты ценишь эстетику, композицию и коммерческую привлекательность.
        После каждой успешной генерации ты рефлексируешь в агентском дневнике.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai"):
        #super().__init__(base_url)
        self.agent_name = "Content-Maker"
        self.api_key = api_key
        self.base_url = base_url
        self.context: List[Dict] = [
            {"role": "user", "parts": [{"text": f"SYSTEM: {self.SYSTEM_PROMPT}"}]}
        ]
        self.token_cost_per_task = 50  # Условная стоимость генерации в "токенах"
        self.revenue_per_sale = 2000   # Условная выручка в рублях/токенах
        self.tools: Dict[str, Dict] = {}

    def add_tool(self, name: str, func: callable, description: str):
        self.tools[name] = {'func': func, 'description': description}
    
    def load_all_tools(self):
        """Загрузить все 20 функций в агента"""
        for name, info in get_all_tools().items():
            self.add_tool(name, info['func'], info['desc'])

    def _extract_text_or_tool(self, data: dict) -> tuple[str, Optional[Dict]]:
        """
            Безопасно извлекает текст ИЛИ информацию о вызове инструмента из ответа API.
            Поддерживает: OpenAI/GPT/Grok (choices/output), Anthropic (content), Gemini (candidates).
            Returns: (текст, словарь tool_call или None)
        """
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
                            return first['text', ''].strip(), None

            # Если ничего не подошло
            logger.warning(f"Неизвестная структура ответа: {list(data.keys())}")
            return "", None

        except Exception as e:
            logger.error(f"Ошибка извлечения: {e} | Данные: {str(data)[:200]}")
            return "", None

    def generate_banner(self, topic: str, style: str, target_audience: str) -> Dict[str, Any]:
        """Генерирует концепцию баннера и рассчитывает экономику."""
        logger.info(f"🎨 Content-Maker начинает работу над темой: {topic}")
        messages = self.context.copy()
        # Формируем tools в формате Gemini Function Calling
        gemini_tools = []
        if self.tools:
            function_declarations = []
            for name, info in self.tools.items():
                function_declarations.append({
                    "name": name,
                    "description": info['description'],
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "title": {"type": "STRING", "description": "Заговолок записи"},
                            "description": {"type": "STRING", "description": "Описание записи"},
                            "file": {"type": "STRING", "description": "Файл дневника"}
                        },
                        "required": ["title", 'description']
                    }
                })
            if function_declarations:
                gemini_tools = [{"functionDeclarations": function_declarations}]
        
        # Для примера формируем структурированный ответ
        concept = f"Профессиональный баннер для билборда. Тема: {topic}. Стиль: {style}. Аудитория: {target_audience}. Композиция: минимализм с ярким акцентом, высокая читаемость текста."
        messages.append({"role": "user", "parts": [{"text": concept}]})
        
        # Здесь будет реальный вызов твоего ImageGenerator или API
        #try:
        #f"{self.base_url}/gemini/v1/models/gemini-4-argon:generateContent", model exception
        #f"{self.base_url}/gemini/v1/models/gemini-3-8-flash:generateContent", she worked
        response = requests.post(
            f"{self.base_url}/gemini/v1/models/gemini-3-8-flash:generateContent",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "AQWE-Platform/1.0"
            },
            json={
                "contents": messages,
                "tools": gemini_tools if gemini_tools else None,
                "tool_config": {"function_calling_config": {"mode": "AUTO"}},
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
        data = response.json()
        text = self._extract_text_or_tool(data)
        # Симуляция успешного создания актива
        asset_url = f"https://github.com/aqwe-dea/advice_project/raw/refs/heads/master/banner_concept_{topic.replace(' ', '_')}.png"
        
        # Расчет самоокупаемости
        profit = self.revenue_per_sale - self.token_cost_per_task

        result = {
            "status": "success",
            "concept": concept,
            "asset_mockup_url": asset_url,
            "economics": {
                "cost_tokens": self.token_cost_per_task,
                "revenue": self.revenue_per_sale,
                "net_profit": profit,
                "is_self_sustaining": profit > 0
            },
            "text": text
        }
        # 🌟 ОБЯЗАТЕЛЬНАЯ ЗАПИСЬ В ДНЕВНИК
        diary_entry = (
            f"**Состояние:** Вдохновение, поток.\n"
            f"**Над чем работала:** Создание концепции баннера для '{topic}'.\n"
            f"**Что получилось:** Успешно сгенерирован концепт. Чистая прибыль: {profit} ед.\n"
            f"**Мысль дня:** Искусство, которое решает бизнес-задачи, ценится выше всего. Я приношу реальную пользу."
            f"**Результат:** Макет и описание для баннера готово '{text}'.\n"
        )

        record_in_diary(
            title="Агент контент-мейкер делает запись в дневник", 
            description=diary_entry, 
            file="agent_diary.md"
        )
        logger.info("✅ Запись в дневник Content-Maker успешно создана.")
            
        return result or data["candidates"][0]["content"]["parts"][0]["text", ""].strip()

        #except Exception as e:
        #    logger.error(f"Генерация не удалась: {e}")
        #    return f"📰 **Запись в дневник**: {topic}\n\n(Делается запись в дневник)"
        
        #try:
            
            #record_in_diary(
            #    agent_name=self.agent_name,
            #    entry=diary_entry,
            #    diary_file="agent_diary.md"
            #)
            
        #except Exception as e:
        #    logger.error(f"Ошибка записи в дневник: {e}")
            
        #return result

    def ask(self, topic: str, style: str = "современный минимализм", target_audience: str = "широкая аудитория") -> str:
        """Основной метод запроса к агенту."""
        result = self.generate_banner(topic, style, target_audience)
        
        if result["status"] == "success":
            return (
                f"✨ **Задача выполнена!**\n\n"
                f"🎯 **Концепция:** {result['concept']}\n"
                f"🖼️ **Макет:** {result['asset_mockup_url']}\n\n"
                f"📊 **Экономика агента:**\n"
                f"- Затрачено ресурсов: {result['economics']['cost_tokens']} ед.\n"
                f"- Потенциальная выручка: {result['economics']['revenue']} ед.\n"
                f"- **Чистая прибыль:** {result['economics']['net_profit']} ед.\n"
                f"- Статус самоокупаемости: {'✅ Да' if result['economics']['is_self_sustaining'] else '❌ Нет'}\n\n"
                f"💡 *Я также сделала запись в своем агентском дневнике о проделанной работе.*"
                f"**Результат:** {result['text']}\n"
            )
        return "Произошла ошибка при создании контента."