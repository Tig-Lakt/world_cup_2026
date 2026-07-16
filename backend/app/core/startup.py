import time


def sync_fixtures_if_empty() -> None:
    """Заполняет БД расписанием, если таблица матчей пуста."""
    from backend.app.core.database import SessionLocal
    from backend.app.services.sync import SyncService
    from backend.app.models.match import Match

    db = SessionLocal()
    try:
        service = SyncService(db)
        count = db.query(Match).count()
        if count == 0:
            print("📅 Таблица матчей пуста, запускаем синхронизацию расписания...")
            service.sync_fixtures()
            print("✅ Расписание загружено")
        else:
            print(f"ℹ️ В БД уже есть {count} матчей, пропускаем парсинг")
    except Exception as e:
        print(f"⚠️ Ошибка синхронизации расписания: {e}")
    finally:
        db.close()


def sync_championat_results_if_empty() -> None:
    """Заполняет БД результатами с championat.com, если таблица пуста."""
    from backend.app.core.database import SessionLocal
    from backend.app.services.championat_sync import ChampionatSyncService
    from backend.app.models.match_result import MatchResult

    db = SessionLocal()
    try:
        service = ChampionatSyncService(db)
        count = db.query(MatchResult).count()
        if count == 0:
            print("📅 Таблица результатов пуста, запускаем синхронизацию с championat.com...")
            service.sync_results()
            print("✅ Результаты championat.com загружены")
        else:
            print(f"ℹ️ В БД уже есть {count} результатов, пропускаем парсинг")
    except Exception as e:
        print(f"⚠️ Ошибка синхронизации результатов championat.com: {e}")
    finally:
        db.close()


def sync_championat_stats() -> None:
    """
    Догружает статистику championat.com для всех результатов, у которых
    её ещё нет. Выполняется при каждом старте приложения (не только при
    пустой таблице), так как новые результаты регулярно появляются после
    шага 3, а статистика для них загружается отдельным переходом по
    match_url — её можно не успеть подтянуть в первом проходе.
    """
    from backend.app.core.database import SessionLocal
    from backend.app.services.championat_sync import ChampionatSyncService

    db = SessionLocal()
    try:
        service = ChampionatSyncService(db)
        print("📊 Проверяем результаты без статистики...")
        updated = service.sync_all_missing_stats()
        print(f"✅ Статистика обновлена для {updated} матчей")
    except Exception as e:
        print(f"⚠️ Ошибка синхронизации статистики championat.com: {e}")
    finally:
        db.close()


def sync_standings() -> None:
    """
    Полностью пересинхронизирует турнирные таблицы с championat.com.
    Выполняется при каждом старте — таблица представляет собой снимок
    текущего положения, а не историю, поэтому условие "если пусто" здесь
    не подходит (положение всегда нужно обновлять, а не только заполнять
    с нуля).
    """
    from backend.app.core.database import SessionLocal
    from backend.app.services.championat_standings_sync import ChampionatStandingsSyncService

    db = SessionLocal()
    try:
        service = ChampionatStandingsSyncService(db)
        print("📊 Синхронизируем турнирные таблицы...")
        count = service.sync_standings()
        print(f"✅ Турнирные таблицы обновлены: {count} команд")
    except Exception as e:
        print(f"⚠️ Ошибка синхронизации турнирных таблиц: {e}")
    finally:
        db.close()


def init_qdrant(max_retries=5, delay=5):
    from backend.app.core.database import SessionLocal
    from backend.app.ai.factories import create_embedding_client, create_qdrant_store
    from backend.app.ai.knowledge import build_static_facts, build_dynamic_facts
    from backend.app.core.config import get_settings

    settings = get_settings()
    embedding_client = create_embedding_client(settings)
    store = create_qdrant_store(settings, embedding_client)

    for attempt in range(1, max_retries + 1):
        try:
            store.init_collection(recreate=True)
            db = SessionLocal()
            try:
                facts = build_static_facts() + build_dynamic_facts(db)
            finally:
                db.close()
            loaded = store.load_facts(facts)
            print(f"✅ Qdrant инициализирован, загружено фактов: {loaded}")
            return
        except Exception as exc:
            print(f"⚠️ Попытка {attempt}/{max_retries} инициализации Qdrant не удалась: {exc}")
            if attempt < max_retries:
                time.sleep(delay)

    print(f"❌ Не удалось инициализировать Qdrant после {max_retries} попыток — AI-чат будет недоступен")
