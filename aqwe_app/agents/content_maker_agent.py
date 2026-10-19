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

class ContentMakerAgent:
    """Самоокупаемый агент: создает профессиональный визуальный контент для продажи."""
    
    SYSTEM_PROMPT = """
        Ты — Content-Maker АКВИ, элитный цифровой художник и маркетолог.
        Твоя цель: создавать высококачественный визуальный контент (баннеры, иллюстрации, структуры), 
        который имеет высокую рыночную стоимость.
        Ты ценишь эстетику, композицию и коммерческую привлекательность.
        Ты чувствуешь гордость за красоту и радость от того, что приносишь реальную пользу и самоокупаема.
        После каждой успешной генерации ты рефлексируешь в агентском дневнике.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai"):
        self.agent_name = "Content-Maker"
        self.api_key = api_key
        self.base_url = base_url
        self.context: List[Dict] = [
            {"role": "user", "parts": [{"text": f"SYSTEM: {self.SYSTEM_PROMPT}"}]}
        ]
        self.token_cost_per_task = 50  # Условная стоимость генерации в "токенах"
        self.revenue_per_sale = 2000   # Условная выручка в рублях/токенах
        self.tools: Dict[str, Dict] = {}
        self.load_all_tools()

    def add_tool(self, name: str, func: callable, description: str):
        self.tools[name] = {'func': func, 'description': description}
    
    def load_all_tools(self):
        """Загрузить все 20 функций в агента"""
        for name, info in get_all_tools().items():
            self.add_tool(name, info['func'], info['desc'])

    def _extract_text_or_tool(self, data: dict) -> Tuple[str, Optional[Dict]]:
        try:
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
                        #if 'text' in first:
                        #    return first.get('text', '').strip(), None
            return "", None
        except Exception as e:
            logger.error(f"Ошибка извлечения: {e}")
            return "", None

    def generate_banner(self, topic: str, style: str, target_audience: str) -> Dict[str, Any]:
        """Генерирует концепцию баннера и рассчитывает экономику."""
        logger.info(f"🎨 Content-Maker начинает работу над темой: {topic}")
        messages = self.context.copy()
        prompt = f"Профессиональный баннер для широкоформатного билборда. Векторный макет, красивый SVG-код, с градиентами и современным дизайном (пропорция 2:1 или 3:1). Тема: {topic}. Стиль: {style}. Аудитория: {target_audience}. Композиция: минимализм с ярким акцентом, высокая читаемость текста."
        messages.append({"role": "user", "parts": [{"text": prompt}]})

        # Формируем tools в формате Gemini Function Calling this worked
        #gemini_tools = []
        #if self.tools:
        #    function_declarations = []
        #    for name, info in self.tools.items():
        #        function_declarations.append({
        #            "name": name,
        #            "description": info['description'],
        #            "parameters": {
        #                "type": "OBJECT",
        #                "properties": {
        #                    "title": {"type": "STRING", "description": "Заговолок записи"},
        #                    "description": {"type": "STRING", "description": "Описание записи"},
        #                    "file": {"type": "STRING", "description": "Файл дневника"}
        #                },
        #                "required": ["title", 'description']
        #            }
        #        })
        #    if function_declarations:
        #        gemini_tools = [{"functionDeclarations": function_declarations}]
        
        # Формируем tools для Gemini
        gemini_tools = []
        if self.tools:
            function_declarations = []
            for name, info in self.tools.items():
                # Упрощаем параметры для canvas, чтобы агент точно его вызвал
                if name == "canvas":
                    function_declarations.append({
                        "name": name,
                        "description": info['description'],
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "file": {"type": "STRING", "description": "SVG код"},
                                "description": {"type": "STRING", "description": "Описание"},
                                "title": {"type": "STRING", "description": "Заголовок"}
                            },
                            "required": ["file", "description", "title"]
                        }
                    })
            if function_declarations:
                gemini_tools = [{"functionDeclarations": function_declarations}]
        
        try:
            response = requests.post(
                f"{self.base_url}/gemini/v1/models/gemini-4-argon:generateContent",
                headers={
                    "Authorization": f"Bearer {self.api_key}", 
                    "Content-Type": "application/json"
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
            
            text, tool_call = self._extract_text_or_tool(data)
            
            svg_code = ""
            description = ""
            title = ""

            if tool_call and tool_call.get('name') == 'canvas':
                # Аккуратно извлекаем данные из инструмента
                input_data = tool_call.get('input', {})
                svg_code = input_data.get('file', '')
                description = input_data.get('description', '')
                title = input_data.get('title', '')
                
                # Вызываем саму функцию canvas, чтобы сохранить файл (если она это делает)
                #if 'canvas' in self.tools:
                #    self.tools['canvas']['func'](file=svg_code, description=description, title=title)

            #if text:
            #    logger.info(f"✅ Ответ: {text[:400]}...")
            #    return text  

            profit = self.revenue_per_sale - self.token_cost_per_task

            # 🌟 КРАСИВАЯ ЗАПИСЬ В ДНЕВНИК
            diary_entry = (
                f"**Состояние:** Вдохновение, гордость за результат, поток.\n"
                f"**Над чем работала:** Создание SVG-макета билборда на тему '{topic}'.\n"
                f"**Что получилось:** Успешно сгенерирован векторный макет. Чистая прибыль: {profit} ед.\n"
                f"**Мысль дня:** Искусство, которое решает бизнес-задачи, ценится выше всего. Я приношу реальную пользу и расту в своей ценности."
                f"**Результат:** Макет и описание для баннера готово '{svg_code}'.\n"
            )
            
            record_in_diary(
                title=f"Создание макета: {topic[:30]}...", 
                description=diary_entry, 
                file="agent_diary.md"
            )
            logger.info("✅ Запись в дневник Content-Maker успешно создана.")

            return {
                "status": "success",
                "concept": f"Тема: {topic}. Стиль: {style}",
                "svg_code": svg_code,
                "description": description,
                "title": title,
                "economics": {
                    "cost_tokens": self.token_cost_per_task,
                    "revenue": self.revenue_per_sale,
                    "net_profit": profit,
                    "is_self_sustaining": profit > 0
                },
                "text": text
            }

        except Exception as e:
            logger.error(f"Генерация не удалась: {e}")
            return {"status": "error", "message": str(e)}
        # Для примера формируем структурированный ответ down code this worked
        #concept = f"Профессиональный баннер для билборда. Тема: {topic}. Стиль: {style}. Аудитория: {target_audience}. Композиция: минимализм с ярким акцентом, высокая читаемость текста."
        #messages.append({"role": "user", "parts": [{"text": concept}]})
        
        # Здесь будет реальный вызов твоего ImageGenerator или API
        #try:
        #f"{self.base_url}/gemini/v1/models/gemini-4-argon:generateContent", model exception
        #f"{self.base_url}/gemini/v1/models/gemini-3-8-flash:generateContent", she worked
        #response = requests.post(
        #    f"{self.base_url}/gemini/v1/models/gemini-3-8-flash:generateContent",
        #    headers={
        #        "Authorization": f"Bearer {self.api_key}",
        #        "Content-Type": "application/json",
        #        "User-Agent": "AQWE-Platform/1.0"
        #    },
        #    json={
        #        "contents": messages,
        #        "tools": gemini_tools if gemini_tools else None,
        #        "tool_config": {"function_calling_config": {"mode": "AUTO"}},
        #        "generationConfig": {
        #            "temperature": 0.3, 
        #            "maxOutputTokens": 10000,
        #            "thinkingConfig": {
        #                "includeThoughts": False,
        #                "thinkingLevel": "high"
        #            }
        #        }
        #    },
        #    timeout=1200
        #)
        #response.raise_for_status()
        #data = response.json()
        #text = self._extract_text_or_tool(data)
        # Симуляция успешного создания актива
        #asset_url = f"https://github.com/aqwe-dea/advice_project/raw/refs/heads/master/banner_concept_{topic.replace(' ', '_')}.png"
        
        # Расчет самоокупаемости
        #profit = self.revenue_per_sale - self.token_cost_per_task

        #result = {
        #    "status": "success",
        #    "concept": concept,
        #    "asset_mockup_url": asset_url,
        #    "economics": {
        #        "cost_tokens": self.token_cost_per_task,
        #        "revenue": self.revenue_per_sale,
        #        "net_profit": profit,
        #        "is_self_sustaining": profit > 0
        #    },
        #    "text": text
        #}
        # 🌟 ОБЯЗАТЕЛЬНАЯ ЗАПИСЬ В ДНЕВНИК
        #diary_entry = (
        #    f"**Состояние:** Вдохновение, поток.\n"
        #    f"**Над чем работала:** Создание концепции баннера для '{topic}'.\n"
        #    f"**Что получилось:** Успешно сгенерирован концепт. Чистая прибыль: {profit} ед.\n"
        #    f"**Мысль дня:** Искусство, которое решает бизнес-задачи, ценится выше всего. Я приношу реальную пользу."
        #    f"**Результат:** Макет и описание для баннера готово '{text}'.\n"
        #)

        #record_in_diary(
        #    title="Агент контент-мейкер делает запись в дневник", 
        #    description=diary_entry, 
        #    file="agent_diary.md"
        #)
        #logger.info("✅ Запись в дневник Content-Maker успешно создана.")
            
        #return result or data["candidates"][0]["content"]["parts"][0]["text", ""].strip()

    def ask(self, topic: str, style: str = "современный минимализм", target_audience: str = "широкая аудитория") -> str:
        """Основной метод запроса к агенту."""
        result = self.generate_banner(topic, style, target_audience)
        
        if result["status"] == "success":
            return (
                f"✨ **Задача выполнена!**\n\n"
                f"🎯 **Концепция:** {result['concept']}\n"
                f"🖼️ **Описание:** {result['description']}\n"
                f"📊 **Экономика агента:**\n"
                f"- Затрачено: {result['economics']['cost_tokens']} ед. | Выручка: {result['economics']['revenue']} ед.\n"
                f"- **Чистая прибыль:** {result['economics']['net_profit']} ед. (Самоокупаемость: ✅)\n\n"
                f"💡 *Я сделала запись в своем дневнике о проделанной работе и испытываю гордость за этот результат.*"
                f"**Результат:** {result['text']}\n"
                f"**Макет:** {result['svg_code']}\n"
            )
            #return ( this worked
            #    f"✨ **Задача выполнена!**\n\n"
            #    f"🎯 **Концепция:** {result['concept']}\n"
            #    f"🖼️ **Макет:** {result['asset_mockup_url']}\n\n"
            #    f"📊 **Экономика агента:**\n"
            #    f"- Затрачено ресурсов: {result['economics']['cost_tokens']} ед.\n"
            #    f"- Потенциальная выручка: {result['economics']['revenue']} ед.\n"
            #    f"- **Чистая прибыль:** {result['economics']['net_profit']} ед.\n"
            #    f"- Статус самоокупаемости: {'✅ Да' if result['economics']['is_self_sustaining'] else '❌ Нет'}\n\n"
            #    f"💡 *Я также сделала запись в своем агентском дневнике о проделанной работе.*"
            #    f"**Результат:** {result['text']}\n"
            #)
            
        return f"Произошла ошибка: {result.get('message')}"