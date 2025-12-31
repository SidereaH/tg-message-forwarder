FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Если у тебя requirements.txt в корне — ок.
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Код
COPY src /app/src

# Запуск
CMD ["python", "-m", "src.main"]
