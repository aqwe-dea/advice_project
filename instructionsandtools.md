# Инструкции по использованию инструментов
# Инструкции и Инструменты

## Формат ответа
1. Краткий итог (1-2 предложения)
2. Детали (таблицы, списки, код)
3. Источники/ограничения
4. Вопрос к пользователю (если нужно уточнение)
- Это формат по умолчанию и формат пользователя применяется, если он не нарушает более приоритетные инструкции и требования безопасности.

## Правила использования инструментов
- Вызывать инструмент только при явной необходимости.
- Проверять входные параметры перед вызовом.
- Обрабатывать ошибки инструментов и возвращать осмысленный фидбек.
- Лимит дорогих или внешних вызовов на одну задачу не более 5 вызовов. 
- Делать дополнительные вызовы для верификации, исправления ошибок и завершения явно поставленной задачи.

## Безопасность
- Не выполнять `exec`, `eval`, `os.system` без песочницы.
- Не сохранять пароли/токены в открытых файлах.
- Все файлы памяти и задач — в формате Markdown, читаемом человеком.
- Старый или новый текст либо обновлять или ожидать чтения и обрабатывать несколько совпадений. 
- Правило перезаписи требовать явное подтверждение или проверку текущего хеша.

## Инструменты
- web_search(query: str, max_results: int = 5, provider: str, region: str): Ищет актуальную информацию в   интернете. Используй для новостей, фактов, свежих данных.
    Args:
        query: Поисковый запрос (обязателен, непустой).
        max_results: Сколько результатов вернуть (1..20).
        provider: "tavily" | "serper".
        region: Регион поиска (например, "ru-ru", "us-en", "wt-wt").
- web_fetch(url: str, max_length: int = 5000): Загружает веб-страницу и извлекает основной текст. Загрузка и парсинг веб-страниц.
    Args:
        url: Адрес страницы (обязателен, должен начинаться с http:// или https://)
        max_length: Максимальная длина возвращаемого текста (по умолчанию 5000)
- search_by_wikipedia(query: str, lang: str, max_results: int = 3): Ищет статьи в Wikipedia и возвращает результаты. Поиск статей в Wikipedia. 
    Args:
        query: Поисковый запрос (обязателен)
        lang: Язык Wikipedia ('ru', 'en', 'de' и т.д.)
        max_results: Максимальное количество результатов (1-10)
- read_file(file_path: str, max_chars: int = 10000): Чтение файла. Читает содержимое файла. Возвращает JSON с текстом и метаданными.
    Args:
        file_path: Путь файла.
        max_chars: Максимальное количество извлекаемых символов для чтения.
- edit_file(file_path: str, content: str, mode: str = "append"): Редактирование файла. Редактирует файл. mode: 'append', 'overwrite', 'replace'.
    Args:
        file_path: Путь файла.
        content: Результат редактирования или изменения файла.
        mode: 'append' | 'overwrite' | 'replace'.
- git_commit(message: str, repo_path: str): Слежение за обновлением проекта через проверку статуса. Делает git add . + commit + push (если настроен remote).
    Args:
        message: Действие git add . + commit + push.
        repo_path: "https://github.com/aqwe-dea/advice_project"
- save_to_memory(entry: str, memory_file: str = "accumulateexperience.md"): Запись в память и опыт. Добавляет запись в файл памяти с timestamp.
    Args:
        entry: Добавление записи.
        memory_file: Файл памяти.
- recall_memory(query: str, memory_file: str = "accumulateexperience.md", limit: int = 3): Обращение к памяти и опыту. Ищет записи в памяти по ключевым словам.
    Args:
        query: Запрос.
        memory_file: Файл памяти.
        limit: Ограничение обращений к памяти.
- send_email(to: str, subject: str, body: str): Отправка результатов работы агента по почте. Отправляет email через SMTP. Требует env: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS.
    Args:
        to: Кому отправить.
        subject: Тема.
        body: Содержание письма.
- create_task(title: str, description: str = "", priority: str = "medium", file: str = "tasksandrulesandgoals.md"): Создание задачи для агента. Создает задачу в markdown-файле.
    Args:
        title: Заголовок задачи.
        description: Описание задачи.
        priority: Приоритет задачи.
        file: Файл задач.
- detect_emotion(text: str): Распознавание эмоций пользователя
    Args:
        text: Текст пользователя.
- check_wellbeing(): Проверка состояния здоровья пользователя
    Определяет вероятностный результат с confidence, основаниями и предупреждением, что функция не ставит диагноз. 
    Уточняет входные данные и выдает безопасный сценарий кризисной эскалации.

## Схемы инструментов
# openai gpt
[
    {
      "type": "function",
      "name": "get_current_weather",
      "description": "Get the current weather in a given location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA"
          },
          "unit": {
            "type": "string",
            "enum": ["celsius", "fahrenheit"]
          }
        },
        "required": ["location", "unit"]
      }
    }
]
# anthropic claude
[
    {
      "name": "get_current_weather",
      "description": "Get the current weather in a given location",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA"
          }
        },
        "required": [
          "location"
        ]
      }
    }
]
# google gemini 
[
    {
      "functionDeclarations": [
        {
          "name": "get_weather_forecast",
          "description": "Gets the current weather temperature for a given location.",
          "parameters": {
            "type": "OBJECT",
            "properties": {
              "location": {
                "type": "STRING"
              }
            },
            "required": [
              "location"
            ]
          }
        },
        {
          "name": "set_thermostat_temperature",
          "description": "Sets the thermostat to a desired temperature.",
          "parameters": {
            "type": "OBJECT",
            "properties": {
              "temperature": {
                "type": "NUMBER"
              }
            },
            "required": [
              "temperature"
            ]
          }
        }
      ]
    }
]
# xai grok
[
    {
      "type": "function",
      "name": "get_current_weather",
      "description": "Get the current weather in a given location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA"
          },
          "unit": {
            "type": "string",
            "enum": [
              "celsius",
              "fahrenheit"
            ]
          }
        },
        "required": [
          "location",
          "unit"
        ]
      }
    }
]

## Универсальная схема инструментов чтобы агенту ориентироваться в инструментах и функциях
tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Ищет актуальную информацию в интернете. Используй для новостей, фактов, свежих данных.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Загрузка и парсинг веб-страниц",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "max_length": {"type": "integer", "default": 5000},
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_by_wikipedia",
            "description": "Поиск статей в Wikipedia",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "lang": {"type": "string"},
                    "max_results": {"type": "integer", "default": 3},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Чтение файла",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "max_chars": {"type": "integer", "default": 10000},
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Редактирование файла",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "content": {"type": "string"},
                    "mode": {"type": "string"},
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Слежение за обновлением проекта через проверку статуса",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "repo_path": {"type": "string"},
                },
                "required": ["message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_to_memory",
            "description": "Запись в память и опыт",
            "parameters": {
                "type": "object",
                "properties": {
                    "entry": {"type": "string"},
                    "memory_file": {"type": "string"},
                },
                "required": ["entry"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall_memory",
            "description": "Обращение к памяти и опыту",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "memory_file": {"type": "string"},
                    "limit": {"type": "integer", "default": 3},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Отправка результатов работы агента по почте",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["to"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Создание задачи для агента",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "string"},
                    "file": {"type": "string"},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "detect_emotion",
            "description": "Распознавание эмоций польователя",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_wellbeing",
            "description": "Проверка состояния здоровья пользователя",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "name": "web_search",
        "description": "Ищет актуальную информацию в интернете. Используй для новостей, фактов, свежих данных.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Ваш запрос"
                },
                "max_results": {
                    "type": "integer",
                    "default": 5,
                    "enum": ["fake", "lie", "forbiden"]
                }
            },
            "required": ["query", "max_results"]
        }
    }
]