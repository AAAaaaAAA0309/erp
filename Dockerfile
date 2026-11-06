# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Сначала копируем только файл с зависимостями, чтобы использовать кэш
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все остальные файлы проекта
COPY . .

# Открываем порт 7860, который ожидает Hugging Face Spaces
EXPOSE 7860

# Команда для запуска вашего FastAPI-приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]