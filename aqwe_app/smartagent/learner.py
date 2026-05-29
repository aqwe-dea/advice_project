from .long_term import LongTermMemory
class ExperienceLearner:
    def __init__(self, memory: LongTermMemory):
        self.memory = memory
    
    def evaluate_action(self, query: str, action: str, result: str, user_feedback: str = None):
        """Оценить действие и запомнить урок"""
        success = self._is_success(result, user_feedback)
        self.memory.store_experience(query, action, result, success)
        return success
    
    def _is_success(self, result: str, feedback: str = None) -> bool:
        """Простая эвристика: если есть код/данные/положительный фидбек — успех"""
        if feedback:
            return "хорошо" in feedback.lower() or "спасибо" in feedback.lower()
        return bool(result and len(result) > 10)  # Не пустой ответ