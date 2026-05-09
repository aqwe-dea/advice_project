import os
import logging
import requests
import re

logger = logging.getLogger(__name__)

class CodeGenerator:
    """Генератор кода через KIE.ai — ПРЯМОЙ ОТВЕТ"""
    
    # ✅ Используем ПОДДЕРЖИВАЕМУЮ модель:
    DEFAULT_MODEL = "claude-opus-4-5"
    
    def __init__(self, api_key: str, base_url: str = "https://api.kie.ai/claude"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _extract_code_from_response(self, data: dict) -> str:
        """Извлекает чистый код из ответа API KIE.ai"""
        
        # Вариант 1: Новый формат — content[0].text с markdown
        content = data.get('content', [])
        if content and isinstance(content, list) and len(content) > 0:
            text_block = content[0].get('text', '')
            if text_block:
                # Удаляем markdown-блоки ```python ... ```
                code = re.sub(r'^```[a-z]*\n?', '', text_block.strip(), flags=re.MULTILINE)
                code = re.sub(r'\n?```$', '', code.strip(), flags=re.MULTILINE)
                return code.strip()
        
        # Вариант 2: OpenAI-стиль — choices[0].message.content
        code = data.get('choices', [{}])[0].get('message', {}).get('content', '')
        if code:
            return re.sub(r'^```[a-z]*\n?', '', code.strip(), flags=re.MULTILINE)
            code = re.sub(r'\n?```$', '', code.strip(), flags=re.MULTILINE)
            return code.strip()
        
        # Вариант 3: Прямые поля
        code = data.get('resultText') or data.get('output') or data.get('code', '')
        if code and isinstance(code, str):
            return re.sub(r'^```[a-z]*\n?', '', code.strip(), flags=re.MULTILINE)
            code = re.sub(r'\n?```$', '', code.strip(), flags=re.MULTILINE)
            return code.strip()
        
        # Вариант 4: Если code — это список (как в твоём ответе)
        if isinstance(code, list) and len(code) > 0:
            text_block = code[0].get('text', '') if isinstance(code[0], dict) else str(code[0])
            if text_block:
                code = re.sub(r'^```[a-z]*\n?', '', text_block.strip(), flags=re.MULTILINE)
                code = re.sub(r'\n?```$', '', code.strip(), flags=re.MULTILINE)
                return code.strip()
        
        return ''
    
    def generate(
        self,
        prompt: str,
        language: str = "python",
        include_comments: bool = True,
        **kwargs
    ) -> dict:
        """Сгенерировать код по описанию — ПРЯМОЙ ЗАПРОС, ПРЯМОЙ ОТВЕТ."""
        
        system_prompt = f"""Ты — профессиональный разработчик на {language}. 
Твоя задача — писать чистый, эффективный, хорошо документированный код.
Отвечай ТОЛЬКО кодом, без лишних объяснений, если не запрошено иное."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # === ✅ ПРАВИЛЬНЫЙ URL (без модели в пути!) ===
            response = requests.post(
                f"{self.base_url}/v1/messages",  # ← Стандартный endpoint!
                headers=self.headers,
                json={
                    "model": self.DEFAULT_MODEL,  # ← Модель только в теле запроса!
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.2,
                    "max_tokens": 4000
                },
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Полный ответ API: {data}")
            
            # === Проверка на ошибку "model not supported" ===
            if data.get('code') == 422 and 'not supported' in str(data.get('msg', '')).lower():
                logger.error(f"Модель {self.DEFAULT_MODEL} не поддерживается")
                return {
                    "success": False, 
                    "error": f"Модель '{self.DEFAULT_MODEL}' не поддерживается. Попробуйте другую."
                }
            
            code = self._extract_code_from_response(data)
            # === Извлечение кода из ответа ===
            # Вариант 1: OpenAI-стиль (наиболее вероятный)
            # code = data.get('content', [{}])
            
            if not code:
                logger.error(f"Не удалось извлечь код из ответа: {data}")
                return {"success": False, "error": "Пустой ответ от API"}
            
            return {
                "success": True,
                "code": code,
                "language": language,
                "prompt": prompt,
                "model": self.DEFAULT_MODEL
            }
            
        except requests.Timeout:
            logger.error("Таймаут запроса к KIE.ai")
            return {"success": False, "error": "Таймаут API"}
        except requests.RequestException as e:
            logger.error(f"Ошибка запроса: {str(e)}")
            return {"success": False, "error": f"Ошибка сети: {str(e)}"}
        except Exception as e:
            logger.error(f"Неизвестная ошибка: {str(e)}", exc_info=True)
            return {"success": False, "error": f"Ошибка: {str(e)}"}