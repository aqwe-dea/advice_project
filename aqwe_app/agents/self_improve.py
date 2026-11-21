import logging
import re
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from pathlib import Path
from abc import abstractmethod

logger = logging.getLogger(__name__)

class SelfImproveLoop:
    """Цикл самоулучшения для агентов"""
    
    def __init__(self, agent, api_key: str, max_iterations: int = 3, base_url: str = "https://api.kie.ai"):
        self.agent = agent
        self.api_key = api_key
        self.base_url = base_url    
        self.max_iterations = max_iterations
        self.metrics = []
    
    def _extract_code_block(self, text: str) -> Optional[str]: 
        """Извлечь Python-код из markdown-блока ```python ... ```"""
        # Исправленное регулярное выражение с re.DOTALL для захвата переносов строк
        match = re.search(r'```python\s*(.*?)\s*```', text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(0).strip()
        return None

    def run(self, test_function: Callable, initial_code: str) -> dict:
        """
            Запустить цикл улучшения.
            Args:
                test_function: Функция, которая тестирует код и возвращает (success: bool, feedback: str)
                initial_code: Исходный код для улучшения
        """
        current_code = initial_code
        last_feedback = "Начальный код требует проверки."

        for iteration in range(self.max_iterations):
            logger.info(f"🔄 Итерация {iteration + 1}/{self.max_iterations}")
            
            # 1. Анализ и запрос на улучшение с учетом прошлого фидбека
            analysis_prompt = f"""
                Ты — эксперт по рефакторингу кода. 
                Предыдущая проверка дала следующий результат: {last_feedback}
            
                Проанализируй этот код и исправь его, учитывая замечания:
                - Оптимизация производительности
                - Улучшение читаемости (PEP 8)
                - Добавление обработки ошибок
                - Лучшие практики

                Текущий код:
                ```python
                {current_code}
                ```
            
                Ответь СТРОГО в формате:
                Краткое объяснение изменений.
                ```python
                [исправленный код здесь]
                ```
            """
            
            # Вызываем метод агента для получения ответа
            agent_instance = self.agent(api_key=self.api_key, base_url=self.base_url)
            text = agent_instance._call_llm(prompt=analysis_prompt)
            
            # 2. Извлечение исправленного кода
            improved_code = self._extract_code_block(text)
            
            if not improved_code:
                logger.warning("⚠️ Не удалось извлечь код из ответа агента. Прерывание цикла.")
                self.metrics.append({"iteration": iteration + 1, "status": "failed_extraction", "feedback": text})
                break
                
            # 3. Тестирование улучшенного кода
            success = improved_code
            feedback = text
            
            self.metrics.append({
                "iteration": iteration + 1, 
                "status": "success" if success else "failed_test",
                "feedback": feedback
            })
            
            if success:
                logger.info(f"✅ Код успешно прошел проверку на итерации {iteration + 1}!")
                current_code = improved_code
                break # Цель достигнута, выходим из цикла
            else:
                logger.warning(f"⚠️ Тест не пройден: {feedback}. Передаем фидбек агенту для следующей итерации.")
                last_feedback = feedback
                current_code = improved_code # Передаем агенту его же последнюю версию для доработки

        return { 
            "final_code": current_code,
            "is_success": success if 'success' in locals() else False,
            "feedback": last_feedback,
            "metrics": self.metrics, 
            "iterations_completed": len(self.metrics) 
        }