from sqlalchemy import Column, Integer, String, DateTime, Float, UniqueConstraint
from sqlalchemy.sql import func

from ..core.database import Base


class Standing(Base):
    """
    Турнирное положение команды в группе ЧМ-2026, источник — championat.com.

    Команда хранится строкой (не FK на teams), как и в MatchResult —
    championat.com не пересекается со справочником команд из
    Flashscore-парсера расписания, написание названий может отличаться.
    """

    __tablename__ = "standings"

    id              = Column(Integer, primary_key=True, index=True)

    group_name      = Column(String(50),  nullable=False)   # "Группа A"
    position        = Column(Integer, nullable=False)        # 1..4
    team_name       = Column(String(100), nullable=False)

    played          = Column(Integer, default=0)
    won             = Column(Integer, default=0)
    drawn           = Column(Integer, default=0)
    lost            = Column(Integer, default=0)

    goals_for       = Column(Integer, default=0)
    goals_against   = Column(Integer, default=0)

    points          = Column(Integer, default=0)
    points_pct      = Column(Float, default=0.0)   # "% очков", например 16.7

    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        # Одна команда — одна строка в одной группе. Перезаписываем
        # существующую запись при каждом обновлении таблицы (см.
        # StandingRepository.replace_all), а не накапливаем дубликаты.
        UniqueConstraint("group_name", "team_name", name="uq_standings_group_team"),
    )

    def __repr__(self) -> str:
        return (
            f"<Standing(group='{self.group_name}', pos={self.position}, "
            f"team='{self.team_name}', pts={self.points})>"
        )