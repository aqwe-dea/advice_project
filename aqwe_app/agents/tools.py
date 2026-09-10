import os
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from .web_fetch import web_fetch
from .web_search import web_search
from .wikipedia_search import search_by_wikipedia
from .functionsforagents.read_file import read_file
from .functionsforagents.edit_file import edit_file
from .functionsforagents.git_commit import git_commit
from .functionsforagents.save_to_memory import save_to_memory
from .functionsforagents.recall_memory import recall_memory
from .functionsforagents.create_task import create_task
from .functionsforagents.send_email import send_email
from .functionsforagents.detect_emotion import detect_emotion
from .functionsforagents.check_wellbeing import check_wellbeing
from .search_internet import search_internet
from ..check_network_connection import check_network_connection
from ..project_inspector import ProjectInspector
from ..file_navigator import list_directory, find_files
from ..code_sandbox import python_sandbox
from ..semantic_memory import semantic_memory_recall
from ..live_canvas import LiveMultimodalWorkspace

def get_all_tools() -> Dict[str, Dict]:
    """Единая точка регистрации всех 20 функций"""
    return {
        # 🔍 Поиск и данные
        "web_search": {"func": web_search, "desc": "Поиск актуальной информации в интернете"},
        "web_fetch": {"func": web_fetch, "desc": "Загрузка и парсинг веб-страниц"},
        "search_by_wikipedia": {"func": search_by_wikipedia, "desc": "Поиск статей в Wikipedia"},
        "search_internet": {"func": search_internet, "desc": "Поиск через Tavily/Serper"},
        
        # 📁 Файлы и проект
        "read_file": {"func": read_file, "desc": "Чтение файла"},
        "edit_file": {"func": edit_file, "desc": "Редактирование файла"},
        "list_directory": {"func": list_directory, "desc": "Получение структуры проекта"},
        "find_files": {"func": find_files, "desc": "Поиск файлов по шаблону"},
        "git_commit": {"func": git_commit, "desc": "Git commit + push"},
        "project_inspector": {"func": ProjectInspector, "desc": "Полная инспекция проекта"},
        
        # 🧠 Память и обучение
        "save_to_memory": {"func": save_to_memory, "desc": "Запись в память и опыт"},
        "recall_memory": {"func": recall_memory, "desc": "Семантический поиск по памяти"},
        "semantic_memory_recall": {"func": semantic_memory_recall, "desc": "Векторный поиск по опыту"},
        
        # 🛠️ Утилиты
        "create_task": {"func": create_task, "desc": "Создание задачи в markdown"},
        "send_email": {"func": send_email, "desc": "Отправка email через SMTP"},
        "detect_emotion": {"func": detect_emotion, "desc": "Распознавание эмоций"},
        "check_wellbeing": {"func": check_wellbeing, "desc": "Проверка состояния пользователя"},
        "check_network_connection": {"func": check_network_connection, "desc": "Проверка интернет-соединения"},
        "python_sandbox": {"func": python_sandbox, "desc": "Безопасное исполнение кода"},
        
        # 🎨 Творчество
        "canvas": {"func": LiveMultimodalWorkspace, "desc": "Живой холст для мультимодального творчества"}
    }