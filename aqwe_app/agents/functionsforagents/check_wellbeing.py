import json

def check_wellbeing() -> str:
    """Возвращает шаблон проверки состояния собеседника. function for check wellbeing health users"""
    return json.dumps({
        "status": "ready",
        "prompts": [
            "Как вы себя чувствуете сегодня? (физически и эмоционально)",
            "Есть ли что-то, что сейчас требует вашего внимания или заботы?",
            "Нужно ли вам пространство для тишины или, наоборот, для разговора?"
        ],
        "action": "ask_user"
    }, ensure_ascii=False)