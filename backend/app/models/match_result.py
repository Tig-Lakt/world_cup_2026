from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from ..core.database import Base


class MatchResult(Base):
    """
    Результат матча ЧМ-2026, спарсенный с championat.com.

    Отдельная таблица от `matches` (Flashscore, этап 1/2) — источники
    независимы, названия команд пишутся по-разному между сайтами, поэтому
    команды здесь хранятся как строки, а не FK на `teams`.
    """

    __tablename__ = "match_results"

    id              = Column(Integer, primary_key=True, index=True)

    # ID матча из URL championat.com (.../match/1310352/) — используется
    # для upsert, аналогично flashscore_id в Match.
    championat_id   = Column(String(20), unique=True, nullable=False)
    match_url       = Column(String(500), nullable=True)

    home_team       = Column(String(100), nullable=False)
    away_team       = Column(String(100), nullable=False)

    # Дата матча, как пришла с сайта (дата+время есть всегда в
    # stat-results__date-time, в отличие от Flashscore — поэтому здесь
    # nullable=False, без fallback-на-None как в Match.match_date).
    match_date      = Column(DateTime(timezone=True), nullable=False)

    # None означает "матч не сыгран" (на сайте отображается как "- : -").
    # Такие строки парсер не сохраняет вообще (см. parse_results), но
    # поле оставлено nullable на случай ручного редактирования/будущих
    # сценариев, где статус матча не равен наличию счёта.
    home_score      = Column(Integer, nullable=True)
    away_score      = Column(Integer, nullable=True)

    group_name      = Column(String(50), nullable=True)   # "Группа A"
    tour_number     = Column(Integer, nullable=True)       # data-tour

    # Статистика матча (stat-graph__row пары "слева/справа"), JSON,
    # аналогично Match.stats. Заполняется отдельным шагом по match_url.
    stats           = Column(JSONB, nullable=True)

    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return (
            f"<MatchResult(id={self.id}, "
            f"{self.home_team} {self.home_score}:{self.away_score} {self.away_team}, "
            f"group='{self.group_name}')>"
        )