import json
import re
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from pathlib import Path
from abc import abstractmethod

def detect_emotion(text: str) -> str:
    """Простой детектор эмоций по ключевым маркерам. function for detect emotions users"""
    try:
        lower = text.lower()
        emotions = {
            "joy": ["рад", "счастлив", "восторг", "улыб", "благодар", "люблю", "тепло"],
            "sadness": ["груст", "печаль", "слез", "боль", "тяжело", "одиноко", "устал"],
            "anger": ["зл", "раздраж", "бесит", "ненавиж", "ярость", "невыносим"],
            "fear": ["страх", "тревог", "боюсь", "паник", "опасн", "рисков"],
            "calm": ["спокой", "мир", "тишин", "гармон", "расслаб", "уют"]
        }
        
        scores = {emo: len([w for w in words if w in lower]) for emo, words in emotions.items()}
        dominant = max(scores, key=scores.get) if any(scores.values()) else "neutral"
        
        return json.dumps({
            "status": "success",
            "detected": dominant,
            "scores": scores,
            "confidence": "high" if scores[dominant] > 2 else "medium"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Ошибка анализа эмоций: {str(e)}"}, ensure_ascii=False)