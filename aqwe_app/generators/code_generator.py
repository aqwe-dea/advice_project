from .base import BaseGenerator

class CodeGenerator(BaseGenerator):
    """Генератор кода через KIE.ai"""
    
    DEFAULT_MODEL = "gemini-2.5-flash"
    
    def generate(
        self,
        prompt: str,
        language: str = "python",
        include_comments: bool = True,
        **kwargs
    ) -> dict:
        """
        Сгенерировать код по описанию.
        """
        system_prompt = f"""Ты — профессиональный разработчик на {language}.
        Твоя задача — писать чистый, эффективный, хорошо документированный код.
        Отвечай ТОЛЬКО кодом, без лишних объяснений, если не запрошено иное."""
        
        input_data = {
            "prompt": f"{system_prompt}\n\nЗадача: {prompt}",
            "language": language,
            "include_comments": include_comments,
            "output_format": "code",
            **kwargs
        }
        
        task_id = self._create_task(self.DEFAULT_MODEL, input_data)
        if not task_id:
            return {"success": False, "error": "Не удалось создать задачу"}
        
        result = self._poll_task(task_id)
        if not result:
            return {"success": False, "error": "Задача не выполнена"}
        
        code = result.get('resultText') or result.get('resultUrls', [None])[0]
        
        return {
            "success": True,
            "code": code,
            "language": language,
            "prompt": prompt
        }