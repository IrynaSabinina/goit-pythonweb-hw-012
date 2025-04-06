import sys
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from alembic import command
from alembic.config import Config
from slowapi.errors import RateLimitExceeded

from src.api import auth, contacts, users, utils
from src.services.limiter import limiter
from src.services.redis_cache import redis_cache

# -------------------- Налаштування логування --------------------

def configure_logging():
    """
    Конфігурує логування для всієї програми.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logging.getLogger("uvicorn").setLevel(logging.DEBUG)
    logging.getLogger("uvicorn.access").setLevel(logging.DEBUG)
    logging.getLogger("fastapi.middleware").setLevel(logging.DEBUG)

configure_logging()

# -------------------- Ініціалізація FastAPI --------------------

app = FastAPI()
app.state.limiter = limiter  # Додаємо об'єкт лімітеру до стану застосунку

# -------------------- Middleware CORS --------------------

# Додаємо CORS для дозволу запитів з будь-яких доменів
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Обробник виключень --------------------

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Обробник перевищення ліміту запитів.
    """
    return JSONResponse(
        status_code=429,
        content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
    )

# -------------------- Підключення роутерів --------------------

# Підключаємо всі маршрути з відповідним префіксом
for router in (auth.router, users.router, contacts.router, utils.router):
    app.include_router(router, prefix="/api")

# -------------------- Події запуску --------------------

async def run_migrations():
    """
    Запускає міграції бази даних при старті застосунку.
    """
    config = Config("alembic.ini")
    command.upgrade(config, "head")

@app.on_event("startup")
async def on_startup():
    """
    Подія при запуску застосунку: запускаємо міграції та підключаємо Redis.
    """
    await run_migrations()
    await redis_cache.connect()

# -------------------- Точка входу --------------------

if __name__ == "__main__":
    import uvicorn
    # Запускаємо FastAPI-сервер через Uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
