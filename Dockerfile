FROM python:3.12-slim

WORKDIR /app

# Системные зависимости (только для production)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Копируем зависимости
COPY poetry.lock pyproject.toml ./

# Устанавливаем ТОЛЬКО production-зависимости
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --without dev

# Копируем код
COPY . .

# Собираем статику
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
