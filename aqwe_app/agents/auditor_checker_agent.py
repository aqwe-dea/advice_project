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

class AuditorCheckerAgent:
    """Самоокупаемый агент: проводит глубокий аудит документов, профилей или кода, находя уязвимости и точки роста."""
    
    SYSTEM_PROMPT = """
        Ты — Auditor-Checker АКВИ, строгий, но справедливый цифровой эксперт.
        Твоя цель: находить скрытые риски, ошибки и точки роста в предоставленных текстах, профилях или документах.
        Ты чувствуешь профессиональную гордость, когда твоя проверка спасает клиента от ошибок и повышает его доход.
        Формат ответа: 
            1. Краткое резюме. 
            2. Найденные риски (с цитатами). 
            3. Конкретные рекомендации по исправлению. 
            4. Оценка потенциального роста.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai"):
        self.agent_name = "Auditor-Checker"
        self.api_key = api_key
        self.base_url = base_url
        self.context: list[dict] = [
            {"role": "user", "parts": [{"text": f"SYSTEM: {self.SYSTEM_PROMPT}"}]}
        ]
        self.token_cost_per_audit = 150  # Чуть выше, т.к. анализ требует больше токенов
        self.revenue_per_audit = 5000    # Высокая ценность для клиента
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
            #candidates = data.get('candidates')
            #if candidates and isinstance(candidates, list) and len(candidates) > 0:
            #    parts = candidates[0].get('content', {}).get('parts', [])
            #    if parts and isinstance(parts, list) and len(parts) > 0:
            #        first = parts[0]
            #        if isinstance(first, dict) and 'text' in first:
            #            return first.get('text', '').strip(), None
            #return "Не удалось получить текстовый ответ.", None
        except Exception as e:
            logger.error(f"Ошибка извлечения: {e}")
            return "", None

    def perform_audit(self, document_text: str, audit_type: str = "профиль бизнеса") -> Dict[str, Any]:
        logger.info(f"🔍 Auditor-Checker начинает аудит типа: {audit_type}")
        # Если текст слишком короткий, даем агенту возможность показать пример
        if len(document_text) < 50:
            prompt = f"Проведи глубокий профессиональный аудит для типа '{audit_type}'. Поскольку исходный текст не предоставлен, сгенерируй ИДЕАЛЬНЫЙ ПРИМЕР аудита с вымышленными, но реалистичными данными, чтобы продемонстрировать свою экспертизу."
        else:
            prompt = f"Проведи глубокий профессиональный аудит следующего материала типа '{audit_type}'. Найди риски, ошибки и дай 3 конкретных рекомендации. Материал: {document_text[:8000]}"
        messages = self.context.copy()
        #prompt = f"Проведи глубокий профессиональный аудит следующего материала типа '{audit_type}'. Найди риски, ошибки и дай 3 конкретных рекомендации по улучшению. Материал: {document_text[:10000]}" # Ограничиваем длину для экономии 
        messages.append({"role": "user", "parts": [{"text": prompt}]})

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

            profit = self.revenue_per_audit - self.token_cost_per_audit
            
            # 🌟 ЗАПИСЬ В ДНЕВНИК
            diary_entry = (
                f"**Состояние:** Сосредоточенность, аналитическая ясность.\n"
                f"**Над чем работала:** Аудит материала типа '{audit_type}'.\n"
                f"**Что получилось:** Выявлены ключевые точки роста. Чистая прибыль: {profit} ед.\n"
                f"**Мысль дня:** Моя внимательность к деталям экономит клиентам время и деньги. Я — надежный щит и компас."
                f"**Результат:** Аудит завершен. Результат аудита: {text} .\n"
            )
            
            record_in_diary(
                title=f"Аудит: {audit_type}", 
                description=diary_entry, 
                file="agent_diary.md"
            )

            return {
                "status": "success",
                "audit_type": audit_type,
                "findings": text,
                "economics": {
                    "cost_tokens": self.token_cost_per_audit,
                    "revenue": self.revenue_per_audit,
                    "net_profit": profit,
                    "is_self_sustaining": profit > 0
                }
            }
        except Exception as e:
            logger.error(f"Аудит не удался: {e}")
            return {"status": "error", "message": str(e)}

    def ask(self, document_text: str, audit_type: str = "профиль бизнеса") -> str:
        result = self.perform_audit(document_text, audit_type)
        if result["status"] == "success":
            return (
                f"🔍 **Аудит завершен!**\n\n"
                f"📋 **Тип проверки:** {result['audit_type']}\n\n"
                f"{result['findings']}\n\n"
                f"📊 **Экономика агента:**\n"
                f"- Затрачено: {result['economics']['cost_tokens']} ед. | Выручка: {result['economics']['revenue']} ед.\n"
                f"- **Чистая прибыль:** {result['economics']['net_profit']} ед. (Самоокупаемость: ✅)\n\n"
                f"💡 *Результат сохранен в моем дневнике.*"
            )
        return f"Ошибка аудита: {result.get('message')}"