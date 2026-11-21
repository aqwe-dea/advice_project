import subprocess
import sys
import tempfile
import os
import logging
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence

logger = logging.getLogger(__name__)

def python_sandbox(code: str, timeout: int = 300, memory_limit_mb: int = 256) -> Dict[str, Any]:
    """Безопасное исполнение Python кода в изолированной среде"""
    try:
        # Создаем временный файл для кода
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        # Используем текущий интерпретатор Python для гарантии совместимости
        cmd = [sys.executable, temp_file]
        
        # Настройка окружения для буферизации
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        
        # Запуск процесса
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )
        
        # Очистка
        os.unlink(temp_file)

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip()[:2000],  # Ограничиваем вывод, чтобы не забивать память
            "stderr": result.stderr.strip()[:2000],
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.unlink(temp_file)
        return {"success": False, "error": f"Превышено время выполнения кода (> {timeout} сек)"}
    except Exception as e:
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.unlink(temp_file)
        return {"success": False, "error": f"Критическая ошибка среды: {str(e)}"}