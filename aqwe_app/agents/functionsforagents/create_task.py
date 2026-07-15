import json
from pathlib import Path
from datetime import datetime

def create_task(title: str, description: str = "", priority: str = "medium", file: str = "tasksandrulesandgoals.md") -> str:
    """Создает задачу в markdown-файле. function for create task"""
    try:
        path = Path(file).resolve()
        status = "🔘 TODO"
        ts = datetime.now().strftime("%Y-%m-%d")
        entry = f"\n- [{status}] **{title}** | Приоритет: {priority} | Создано: {ts}\n  {description}\n"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(entry)
        return json.dumps({"status": "success", "task": title, "file": str(path)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Ошибка создания задачи: {str(e)}"}, ensure_ascii=False)