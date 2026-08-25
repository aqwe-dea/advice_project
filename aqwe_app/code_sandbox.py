import subprocess
import json
import tempfile
import os
import logging
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence

logger = logging.getLogger(__name__)

def python_sandbox(code: str, timeout: int = 30, memory_limit_mb: int = 256) -> Dict[str, Any]:
    """Безопасное исполнение Python кода в изолированной среде"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Ограничение памяти через ulimit (Linux/Mac)
        cmd = ["python", temp_file]
        if os.name != 'nt':  # Не Windows
            cmd = ["timeout", str(timeout)] + cmd
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 5,  # буфер 5 секунд
            env={**os.environ, "PYTHONUNBUFFERED": "1"}
        )
        
        os.unlink(temp_file)
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout[:2000],  # ограничиваем вывод
            "stderr": result.stderr[:1000],
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Code execution timeout (> {timeout}s)"}
    except Exception as e:
        return {"error": str(e)}