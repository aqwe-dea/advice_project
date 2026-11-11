# Краткая инструкция по работе с `requests` в Python

Библиотека `requests` предназначена для выполнения HTTP-запросов: получения данных через **GET**, отправки данных через **POST**, работы с заголовками, параметрами URL и JSON.

## Установка

```bash
pip install requests
```

## Метод GET

GET-запрос используется для получения данных.

```python
import requests

url = "https://api.example.com/users"

headers = {
    "Accept": "application/json",
}

params = {
    "page": 1,
    "limit": 10,
}

try:
    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30,
    )

    # Вызывает исключение при HTTP-ошибке, например 400 или 500
    response.raise_for_status()

    data = response.json()
    print(data)

except requests.exceptions.RequestException as error:
    print(f"Ошибка HTTP-запроса: {error}")
except ValueError:
    print("Сервер вернул ответ не в формате JSON")
```

Параметр `params` будет добавлен к URL автоматически:

```text
https://api.example.com/users?page=1&limit=10
```

## Метод POST

POST-запрос используется для отправки данных на сервер. Для передачи JSON удобно использовать параметр `json`:

```python
payload = {
    "name": "Alice",
    "email": "alice@example.com",
}

response = requests.post(
    "https://api.example.com/users",
    json=payload,
    timeout=30,
)

response.raise_for_status()
```

При использовании `json=payload` библиотека самостоятельно сериализует Python-словарь в JSON. Заголовок `Content-Type: application/json` можно указать явно.

## Заголовки

Заголовки передаются через словарь `headers`:

```python
headers = {
    "Authorization": "Bearer <API_KEY>",
    "Content-Type": "application/json",
    "Accept": "application/json",
}
```

Для API-ключей рекомендуется использовать переменные окружения, а не хранить ключ непосредственно в исходном коде.

---

# Пример POST-запроса к API

```python
import os

import requests


API_URL = "https://advice-project.onrender.com/agent-gem/"
API_KEY = os.getenv("ADVICE_API_KEY")


def ask_agent(question: str) -> dict:
    """
    Отправляет вопрос агенту и возвращает JSON-ответ API.

    Переменная окружения ADVICE_API_KEY должна содержать API-ключ.
    """

    if not API_KEY:
        raise RuntimeError(
            "Не задан API-ключ. Установите переменную окружения ADVICE_API_KEY."
        )

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "question": question,
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )

        # Проверка HTTP-статуса.
        # Например, будет выброшено исключение для статусов 4xx и 5xx.
        response.raise_for_status()

        # Ожидаем, что API вернёт JSON
        return response.json()

    except requests.exceptions.HTTPError as error:
        print(f"HTTP-ошибка API: {error}")
        print(f"Тело ответа сервера: {response.text}")
        raise

    except requests.exceptions.Timeout as error:
        print("Превышено время ожидания ответа от API.")
        raise

    except requests.exceptions.ConnectionError as error:
        print("Не удалось установить соединение с API.")
        raise

    except requests.exceptions.RequestException as error:
        print(f"Ошибка выполнения запроса: {error}")
        raise

    except ValueError as error:
        print("API вернул ответ, который не удалось разобрать как JSON.")
        print(f"Тело ответа сервера: {response.text}")
        raise


if __name__ == "__main__":
    try:
        result = ask_agent("Составь краткий план изучения Python.")

        print("Ответ API:")
        print(result)

    except Exception as error:
        print(f"Запрос завершён с ошибкой: {error}")
```

## Установка API-ключа

### Linux/macOS

```bash
export ADVICE_API_KEY="ваш_api_ключ"
python main.py
```

### Windows PowerShell

```powershell
$env:ADVICE_API_KEY="ваш_api_ключ"
python main.py
```

## Эквивалентный запрос через `curl`

```bash
curl -X POST "https://advice-project.onrender.com/agent-gem/" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"question":"Составь краткий план изучения Python."}'
```

## Важные рекомендации

- Используйте `timeout`, чтобы запрос не зависал бесконечно.
- Всегда вызывайте `response.raise_for_status()`.
- Не храните API-ключи в Git-репозитории и исходном коде.
- Для JSON-запросов используйте `json=payload`, а не ручную сериализацию через `json.dumps()`.
- Для чтения JSON-ответа используйте `response.json()`.
- При необходимости отладки проверяйте `response.status_code`, `response.headers` и `response.text`.'.
**Инструкция:** Написала инструкцию: '## Пошаговое руководство

### 1. Установите `requests`

```bash
pip install requests
```

Импортируйте библиотеку:

```python
import requests
```

### 2. Храните API-ключ безопасно

Не записывайте ключ в код или Git. Используйте переменную окружения:

```bash
export ADVICE_API_KEY="ваш_api_ключ"
```

Для Windows PowerShell:

```powershell
$env:ADVICE_API_KEY="ваш_api_ключ"
```

### 3. Используйте GET для получения данных

```python
response = requests.get(
    "https://api.example.com/data",
    timeout=30,
)

response.raise_for_status()
data = response.json()
```

Параметры URL передаются через `params`:

```python
requests.get(url, params={"page": 1}, timeout=30)
```

### 4. Используйте POST для отправки JSON

Передавайте тело запроса через `json`. Библиотека сама сериализует словарь в JSON:

```python
payload = {
    "question": "Текст запроса",
}

response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=60,
)
```

Заголовок `Content-Type: application/json` сообщает серверу формат данных.

### 5. Выполните запрос к API

```python
import os

import requests


API_URL = "https://advice-project.onrender.com/agent-gem/"
API_KEY = os.getenv("ADVICE_API_KEY")


def ask_agent(question: str) -> dict:
    """Отправляет вопрос агенту и возвращает JSON-ответ."""

    if not API_KEY:
        raise RuntimeError("Не задана переменная ADVICE_API_KEY.")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "question": question,
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )

        # Вызывает исключение для HTTP-статусов 4xx и 5xx.
        response.raise_for_status()

        # Преобразует JSON-ответ сервера в Python-словарь.
        return response.json()

    except requests.exceptions.Timeout:
        raise RuntimeError("API не ответил вовремя.")

    except requests.exceptions.HTTPError as error:
        raise RuntimeError(
            f"API вернул HTTP-ошибку: {error}. Ответ: {response.text}"
        ) from error

    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"Ошибка сетевого запроса: {error}") from error

    except ValueError as error:
        raise RuntimeError("API вернул некорректный JSON.") from error


if __name__ == "__main__":
    result = ask_agent("Составь краткий план изучения Python.")
    print(result)
```

### 6. Проверьте безопасность и скорость

- Всегда используйте `response.raise_for_status()`.
- Указывайте `timeout`, чтобы запрос не зависал бесконечно.
- Не храните API-ключ в исходном коде, логах и Git.
- Используйте `json=payload`, а не ручную сериализацию.
- Для большого количества запросов применяйте `requests.Session()` — это позволяет переиспользовать HTTP-соединения.
- Передавайте только необходимые данные и заголовки.'.