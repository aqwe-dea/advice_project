import json
import subprocess
import os
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from pathlib import Path
from abc import abstractmethod

def git_commit(message: str, repo_path: str = "https://github.com/aqwe-dea/advice_project") -> str:
    """Делает git add . + commit + push (если настроен remote). function tracking commit on github"""
    try:
        os.chdir(repo_path)
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        res = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True)
        if res.returncode != 0:
            return json.dumps({"status": "info", "message": "Нет изменений для коммита"}, ensure_ascii=False)
        
        push = subprocess.run(["git", "push"], capture_output=True, text=True)
        return json.dumps({
            "status": "success",
            "commit": message,
            "push_output": push.stdout.strip()[:200]
        }, ensure_ascii=False)
    except FileNotFoundError:
        return json.dumps({"error": "Git не установлен или не в PATH"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Git ошибка: {str(e)}"}, ensure_ascii=False)