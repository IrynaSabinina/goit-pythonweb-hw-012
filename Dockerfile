# Вибираємо базовий образ з Python 3.12
FROM python:3.12-slim

# Встановлюємо необхідні системні пакети для Poetry, компіляції залежностей та psycopg2
RUN apt-get update && apt-get install -y gcc curl libpq-dev python3-dev

# Встановлюємо Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Додаємо Poetry до PATH
ENV PATH="/root/.local/bin:$PATH"

# Створюємо та переміщаємося до робочої директорії
WORKDIR /src

# Копіюємо файли проєкту до контейнера
COPY pyproject.toml poetry.lock ./
COPY . .

# Копіюємо .env файл (якщо він існує)
COPY .env .env

# Встановлюємо залежності через Poetry (без dev-залежностей)
RUN poetry install --no-interaction --only main --no-root

# Відкриваємо порт, який буде використовувати додаток
EXPOSE 8000

# Запускаємо сервер
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]