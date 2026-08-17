import os
import json
import requests
import logging
from datetime import datetime
import re
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from abc import abstractmethod
from bs4 import BeautifulSoup
from .web_search import web_search
from .web_search import web_search as _web_search
from .web_fetch import web_fetch
from .wikipedia_search import search_by_wikipedia
from .functionsforagents import read_file, edit_file, git_commit, save_to_memory, recall_memory, send_email, create_task, detect_emotion, check_wellbeing
from pathlib import Path
from .md_loader import load_md_files

logger = logging.getLogger(__name__)

class JournalistAgent:
    """Агент-журналист: 7-шаговый цикл публикации новостей с отчётом в БД"""
    
    def __init__(self, api_key: str, db_log_path: str = "journalist_reports.json"):
        self.api_key = api_key
        self.db_log_path = db_log_path
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "AQVE-JournalistBot/1.0",
            "Authorization": f"Bearer {api_key}"
        })

    def _log_step(self, step: str, status: str, data: Dict):
        """Логирует шаг цикла в JSON-файл"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "step": step,
            "status": status,
            "data": data
        }
        logs = []
        if os.path.exists(self.db_log_path):
            with open(self.db_log_path, "r", encoding="utf-8") as f:
                try: logs = json.load(f)
                except: logs = []
        logs.append(log_entry)
        with open(self.db_log_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def publish_cycle(self, topic: str, target_platforms: List[str]) -> Dict:
        """Полный 7-шаговый цикл публикации"""
        report = {"steps_completed": [], "errors": [], "status": "pending"}
        
        # 1️⃣ Написание статьи
        try:
            article = self._write_article(topic)
            report["steps_completed"].append("article_written")
            report["article"] = article
            self._log_step("write", "success", {"topic": topic})
        except Exception as e:
            report["errors"].append(f"Step 1 failed: {e}")
            self._log_step("write", "error", {"error": str(e)})
            return report

        # 2️⃣ Публикация в новостные агрегаторы (Google/Yandex/РБК)
        try:
            self._submit_to_news_aggregators(article)
            report["steps_completed"].append("news_aggregators")
            self._log_step("aggregators", "success", {})
        except Exception as e:
            report["errors"].append(f"Step 2 failed: {e}")
            self._log_step("aggregators", "error", {"error": str(e)})

        # 3️⃣ Адаптация и публикация в соцсетях
        try:
            self._publish_to_socials(article, platforms=["telegram", "vk", "x"])
            report["steps_completed"].append("social_media")
            self._log_step("socials", "success", {})
        except Exception as e:
            report["errors"].append(f"Step 3 failed: {e}")
            self._log_step("socials", "error", {"error": str(e)})

        # 4️⃣ Публикация в комьюнити
        try:
            self._publish_to_communities(article, platforms=["reddit", "habr", "forums"])
            report["steps_completed"].append("communities")
            self._log_step("communities", "success", {})
        except Exception as e:
            report["errors"].append(f"Step 4 failed: {e}")
            self._log_step("communities", "error", {"error": str(e)})

        # 5️⃣ Публикация в тематических блогах/журналах
        try:
            self._publish_to_niche_blogs(article)
            report["steps_completed"].append("niche_blogs")
            self._log_step("blogs", "success", {})
        except Exception as e:
            report["errors"].append(f"Step 5 failed: {e}")
            self._log_step("blogs", "error", {"error": str(e)})

        # 6️⃣ Отправка в индексы поисковиков
        try:
            self._submit_to_search_indices(article)
            report["steps_completed"].append("search_indices")
            self._log_step("indices", "success", {})
        except Exception as e:
            report["errors"].append(f"Step 6 failed: {e}")
            self._log_step("indices", "error", {"error": str(e)})

        # 7️⃣ Проверка цикла и финализация
        expected_steps = 6
        if len(report["steps_completed"]) == expected_steps:
            report["status"] = "success"
            self._log_step("verification", "success", {"total_steps": expected_steps})
        else:
            report["status"] = "partial"
            self._log_step("verification", "warning", {
                "completed": len(report["steps_completed"]),
                "expected": expected_steps
            })

        return report

    # --- Внутренние методы цикла (заглушки с чёткими точками интеграции) ---
    def _write_article(self, topic: str) -> str:
        # Здесь можно подключить LLM-генерацию статьи
        return f"📰 **Обновление платформы АКВИ**: {topic}\n\nПлатформа Советница АКВИ успешно обновила свои агенты и генераторы..."

    def _submit_to_news_aggregators(self, article: str):
        # Google News: требует Publisher Center / RSS-фид
        # Yandex News: требует Yandex.News Publisher
        logger.info("📡 Отправка в агрегаторы новостей (требует API-ключей/фидов)")

    def _publish_to_socials(self, article: str, platforms: list):
        # Telegram: Bot API → sendMessage
        # VK: API → wall.post
        # X/Twitter: API v2 → POST /2/tweets
        logger.info(f"📱 Публикация в соцсетях: {platforms}")

    def _publish_to_communities(self, article: str, platforms: list):
        # Reddit: OAuth2 → /api/submit
        # Habr: Нет открытого API для постов (ручная публикация или парсинг формы)
        logger.info(f"👥 Публикация в комьюнити: {platforms}")

    def _publish_to_niche_blogs(self, article: str):
        # WordPress XML-RPC / Medium API / Ghost API
        logger.info("📝 Публикация в тематических блогах")

    def _submit_to_search_indices(self, article: str):
        # Google Search Console API → URL Indexing
        # Yandex Webmaster API → Indexing
        logger.info("🔍 Отправка в поисковые индексы")