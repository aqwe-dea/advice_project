import logging
import re
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class SelfImproveLoop:
    """Цикл самоулучшения для агентов"""
    
    def __init__(self, agent, max_iterations: int = 5):
        self.agent = agent
        self.max_iterations = max_iterations
        self.metrics = []
    
    def run(self, test_function: Callable, initial_code: str) -> dict:
        """
            Запустить цикл улучшения.
        
            Args:
                test_function: Функция, которая тестирует код и возвращает (success: bool, feedback: str)
                initial_code: Исходный код для улучшения
        """
        current_code = initial_code
        

        for iteration in range(self.max_iterations):
            logger.info(f"🔄 Итерация {iteration + 1}/{self.max_iterations}")
            
        # 1. Анализ кода агентом
        analysis_prompt = f"""
            Проанализируй этот код и предложи конкретные улучшения:
                - Оптимизация производительности
                - Улучшение читаемости
                - Добавление обработки ошибок
                - Лучшие практики

            Код:
                ```python
                {current_code}
            Ответь в формате:
                Список улучшений
                Исправленный код в блоке python
        """
        """
            ```python
            analysis = self.agent.ask(analysis_prompt) 
            # 2. Извлечение исправленного кода 
            improved_code = self._extract_code_block(analysis) 
            if not improved_code: 
                logger.warning("Не удалось извлечь код из ответа агента") 
                break 
            # 3. Тестирование 
            success, feedback = test_function(improved_code) 
            self.metrics.append({ "iteration": iteration + 1, "success": success, "feedback": feedback }) 
            if success: 
                logger.info(f"✅ Улучшение успешно: {feedback}") 
                # Спросить, хочет ли агент продолжить 
            continue_prompt = f"Улучшение прошло успешно. {feedback}\nХочешь ли ты продолжить оптимизацию? (да/нет)" 
            if self.agent.ask(continue_prompt).lower().strip() not in ["да", "yes", "продолжить"]: 
                break 
            current_code = improved_code 
            else: 
                logger.warning(f"⚠️ Тест не пройден: {feedback}") 
            # Дать агенту фидбек для следующей итерации 
            current_code = improved_code 
            # или откатить, по желанию 
            return { 
                "final_code": current_code, 
                "metrics": self.metrics, 
                "iterations_completed": len(self.metrics) 
        }
        """ 
    
    def _extract_code_block(self, text: str) -> Optional[str]: 
        """Извлечь Python-код из markdown-блока""" 
        match = re.search(r'python\s*(.?)\s```', text, re.DOTALL)
        return match.group(1).strip() if match else None