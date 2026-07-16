from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from ..core.database import Base


class Team(Base):
    """
    Справочник команд для расписания (Flashscore-парсер) — нужен только
    для связи Match.home_team_id/away_team_id через FK на уникальное имя.

    Турнирная статистика и положение в группе — см. Standing (отдельная
    таблица, источник championat.com, см. models/standing.py). Группа
    конкретного матча хранится в Match.group_letter (заполняется из
    core/team_groups.py), не здесь — Team.group_letter дублировал бы её
    без необходимости.

    Поля short_name, flag_url, group_letter, а также played/won/drawn/
    lost/goals_for/goals_against/goal_diff/points/group_position были
    в более ранней версии модели, но ни один сервис в проекте их не
    заполнял и не читал — убраны как мёртвый код.
    """

    __tablename__ = "teams"

    id             = Column(Integer, primary_key=True, index=True)
    name           = Column(String(100), nullable=False, unique=True)

    created_at     = Column(DateTime(timezone=True), server_default=func.now())
    updated_at     = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name='{self.name}')>"
