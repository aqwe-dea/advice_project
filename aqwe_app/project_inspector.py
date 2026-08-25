import os
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence

logger = logging.getLogger(__name__)

class ProjectInspector:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        
    def inspect_project(self) -> Dict[str, Any]:
        """Полная инспекция проекта: структура, состояние репозитория, зависимости"""
        return {
            "structure": self._get_structure(),
            "git_status": self._get_git_status(),
            "dependencies": self._get_dependencies(),
            "test_results": self._run_tests(),
            "lint_results": self._run_linter()
        }
    
    def _get_structure(self) -> Dict:
        """Древовидная структура проекта"""
        structure = {"root": str(self.project_root), "files": [], "dirs": []}
        for root, dirs, files in os.walk(self.project_root):
            if any(x in root for x in [".git", "__pycache__", "node_modules", ".venv"]):
                continue
            rel_path = Path(root).relative_to(self.project_root)
            structure["dirs"].append(str(rel_path))
            structure["files"].extend([str(rel_path / f) for f in files if not f.startswith(".")])
        return structure
    
    def _get_git_status(self) -> Dict:
        """Статус git репозитория"""
        try:
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                cwd=self.project_root, 
                text=True
            ).strip()

            status = subprocess.check_output(
                ["git", "status", "--porcelain"], 
                cwd=self.project_root, 
                text=True
            ).strip()

            return {
                "branch": branch,
                "has_changes": bool(status),
                "modified_files": [line.split()[1] for line in status.split("\n") if line]
            }
        except:
            return {"error": "Not a git repository"}
    
    def _get_dependencies(self) -> List[str]:
        """Список зависимостей из requirements.txt"""
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            return [line.strip() for line in req_file.read_text().split("\n") if line.strip() and not line.startswith("#")]
        return []
    
    def _run_tests(self) -> Dict:
        """Запуск тестов в песочнице"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--tb=short", "-q"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout[-500:],  # последние 500 символов
                "errors": result.stderr[-500:]
            }
        except subprocess.TimeoutExpired:
            return {"error": "Tests timeout (>60s)"}
        except Exception as e:
            return {"error": str(e)}
    
    def _run_linter(self) -> Dict:
        """Запуск линтера (flake8)"""
        try:
            result = subprocess.run(
                ["flake8", "--max-line-length=120", "--ignore=E203,W503"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "issues": result.stdout.split("\n")[:20]  # первые 20 проблем
            }
        except:
            return {"error": "Flake8 not installed or timeout"}

# Экспорт как функция для агента
def project_inspect_and_verify(project_root: str = ".") -> str:
    inspector = ProjectInspector(project_root)
    result = inspector.inspect_project()
    return json.dumps(result, ensure_ascii=False, indent=2)