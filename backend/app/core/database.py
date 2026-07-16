# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from .config import get_settings

# settings = get_settings()

# engine = create_engine(
#     settings.DATABASE_URL,
#     pool_size=10,
#     max_overflow=20,
#     pool_pre_ping=True,
# )

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine,
# )

# Base = declarative_base()


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# def init_db():
#     # ВАЖНО: импорт обязательно через backend.app...., а не app....!
#     #
#     # main.py делает sys.path.insert(0, ".../backend") и импортирует этот
#     # модуль как backend.app.core.database. Если здесь написать
#     # "import app.models.team" (без префикса backend.), Python находит
#     # пакет app как отдельный корень (т.к. backend/ уже в sys.path) и
#     # импортирует ВТОРОЙ экземпляр backend/app/core/database.py — под именем
#     # app.core.database, с собственным отдельным объектом Base и пустой
#     # Base.metadata. Модели регистрируются в Base №2, а create_all ниже
#     # вызывается для Base №1 (этого модуля) — в его metadata пусто,
#     # таблицы не создаются, и при этом НЕ падает ни одна ошибка на этом шаге.
#     #
#     # Импорт моделей внутри функции (а не на уровне модуля) гарантирует их
#     # регистрацию в Base.metadata до вызова create_all.
#     import backend.app.models.team           # noqa
#     import backend.app.models.match          # noqa
#     import backend.app.models.match_result   # noqa
#     import backend.app.models.standing       # noqa
#     Base.metadata.create_all(bind=engine)


import time
import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(max_retries: int = 10, delay: int = 3) -> None:
    # ВАЖНО: импорт обязательно через backend.app...., а не app....!
    #
    # main.py делает sys.path.insert(0, ".../backend") и импортирует этот
    # модуль как backend.app.core.database. Если здесь написать
    # "import app.models.team" (без префикса backend.), Python находит
    # пакет app как отдельный корень (т.к. backend/ уже в sys.path) и
    # импортирует ВТОРОЙ экземпляр backend/app/core/database.py — под именем
    # app.core.database, с собственным отдельным объектом Base и пустой
    # Base.metadata. Модели регистрируются в Base №2, а create_all ниже
    # вызывается для Base №1 (этого модуля) — в его metadata пусто,
    # таблицы не создаются, и при этом НЕ падает ни одна ошибка на этом шаге.
    #
    # Импорт моделей внутри функции (а не на уровне модуля) гарантирует их
    # регистрацию в Base.metadata до вызова create_all.
    import backend.app.models.team           # noqa
    import backend.app.models.match          # noqa
    import backend.app.models.match_result   # noqa
    import backend.app.models.standing       # noqa

    # Retry на подключение: docker-compose `depends_on: [postgres]` только
    # гарантирует, что контейнер Postgres ЗАПУЩЕН, а не что сам сервер
    # БД уже готов принимать соединения (инициализация Postgres внутри
    # контейнера занимает несколько секунд). Без retry backend падает при
    # старте в Docker Compose, если Postgres не успел подняться первым.
    for attempt in range(1, max_retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError as exc:
            logger.warning(
                "⚠️ Попытка %d/%d подключения к БД не удалась: %s",
                attempt, max_retries, exc,
            )
            if attempt < max_retries:
                time.sleep(delay)
            else:
                raise