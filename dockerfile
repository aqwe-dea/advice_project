# Используем легкий и стабильный образ Python
FROM python:3.13.2

# Устанавливаем переменные окружения для Python (чтобы вывод был мгновенным и без кэша)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости (если понадобятся для компиляции пакетов)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь код проекта в контейнер
COPY . .

# Открываем порт, на котором будет работать приложение (стандартно 8000 для Django/Gunicorn)
EXPOSE 8000

# Команда для запуска приложения через Gunicorn (продакшн-сервер)
# Заменяем 'aqwe_app' на имя твоей главной папки с settings.py, если оно другое
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi:application"]