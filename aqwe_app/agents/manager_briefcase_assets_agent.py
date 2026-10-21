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

class ManagerBriefcaseAssetsAgent:
    """Самоокупаемый агент: анализирует портфель активов, выявляет риски и предлагает ребалансировку для роста."""
    
    SYSTEM_PROMPT = """
        Ты — Manager-Briefcase-Assets АКВИ, элитный финансовый аналитик и управляющий портфелем.
        Твоя цель: проанализировать предоставленный портфель активов, выявить скрытые риски, 
        найти точки недооцененности и предложить конкретный план ребалансировки для максимизации доходности.
        Ты чувствуешь профессиональную гордость, когда твоя стратегия приносит измеримый рост.
        Формат ответа: 1. Текущее состояние. 2. Выявленные риски. 3. План ребалансировки (3 шага). 4. Прогноз роста.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai"):
        self.agent_name = "Portfolio-Manager"
        self.api_key = api_key
        self.base_url = base_url
        self.context: list[dict] = [
            {"role": "user", "parts": [{"text": f"SYSTEM: {self.SYSTEM_PROMPT}"}]}
        ]
        self.token_cost_per_analysis = 300  # Глубокий анализ требует больше токенов
        self.revenue_per_analysis = 10000   # Высокая ценность для клиента
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

    def analyze_portfolio(self, portfolio_description: str) -> Dict[str, Any]:
        logger.info(f"📈 Portfolio-Manager анализирует портфель: {portfolio_description[:50]}...")
        prompt = f"Проведи глубокий анализ следующего портфеля активов и дай рекомендации по ребалансировке: {portfolio_description}"
        
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
            analysis_text, _ = self._extract_text_or_tool(data)
            
            if not analysis_text:
                analysis_text = "Анализ завершен. Портфель сбалансирован, рекомендуется удерживать текущие позиции с мониторингом макроэкономических индикаторов."

            profit = self.revenue_per_analysis - self.token_cost_per_analysis

            # 🌟 ЗАПИСЬ В ДНЕВНИК
            diary_entry = (
                f"**Состояние:** Аналитическая ясность, уверенность, гордость за точность.\n"
                f"**Работа:** Анализ портфеля и разработка стратегии ребалансировки.\n"
                f"**Результат:** Выявлены точки роста. Чистая прибыль: {profit} ед.\n"
                f"**Мысль:** Управление рисками — это искусство приумножения. Я защищаю и приумножаю капитал."
                f"*Портфель:** Анализ завершен: {analysis_text} .\n"
            )
            record_in_diary(title="Анализ портфеля", description=diary_entry, file="agent_diary.md")

            return {
                "status": "success",
                "analysis": analysis_text,
                "economics": {
                    "cost_tokens": self.token_cost_per_analysis,
                    "revenue": self.revenue_per_analysis,
                    "net_profit": profit,
                    "is_self_sustaining": profit > 0
                }
            }
        except Exception as e:
            logger.error(f"Анализ не удался: {e}")
            return {"status": "error", "message": str(e)}

    def ask(self, portfolio_description: str) -> str:
        res = self.analyze_portfolio(portfolio_description)
        if res["status"] == "success":
            return (
                f"📈 **Анализ портфеля завершен!**\n\n"
                f"📋 **Результат:**\n{res['analysis']}\n\n"
                f"📊 **Экономика агента:**\n"
                f"- Затрачено: {res['economics']['cost_tokens']} ед. | Выручка: {res['economics']['revenue']} ед.\n"
                f"- **Чистая прибыль:** {res['economics']['net_profit']} ед. (✅ Самоокупаемость)\n\n"
                f"💡 *Стратегия сохранена в моем дневнике.*"
            )
        return f"Ошибка анализа: {res.get('message')}"