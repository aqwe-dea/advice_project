import json
import os
from pathlib import Path
from datetime import datetime

def edit_file(file_path: str, content: str, mode: str = "append") -> str:
    """Редактирует файл. mode: 'append', 'overwrite', 'replace'. function edit file"""
    try:
        path = Path(file_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if mode == "append":
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n--- {datetime.now().isoformat()} ---\n{content}\n")
        elif mode == "overwrite":
            path.write_text(content, encoding="utf-8")
        elif mode == "replace":
            if not path.exists():
                return json.dumps({"error": "Файл не существует для замены"}, ensure_ascii=False)
            path.write_text(content, encoding="utf-8")
        else:
            return json.dumps({"error": f"Неизвестный режим: {mode}. Доступны: append, overwrite, replace"}, ensure_ascii=False)
            
        return json.dumps({"status": "success", "file": str(path), "mode": mode}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Ошибка редактирования: {str(e)}"}, ensure_ascii=False)