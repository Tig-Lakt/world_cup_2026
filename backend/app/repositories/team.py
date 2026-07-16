from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.team import Team


class TeamRepository:
    """
    Справочник команд для расписания (Flashscore-парсер). Турнирная
    статистика и положение в группе — см. StandingRepository
    (championat.com) — Team не хранит эти данные, см. models/team.py.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, team_id: int) -> Optional[Team]:
        return self.db.query(Team).filter(Team.id == team_id).first()

    def get_by_name(self, name: str) -> Optional[Team]:
        return self.db.query(Team).filter(Team.name == name).first()

    def get_or_create(self, name: str, **kwargs) -> Team:
        """Найти команду по имени или создать новую."""
        team = self.get_by_name(name)
        if team is None:
            team = Team(name=name, **kwargs)
            self.db.add(team)
            self.db.flush()
        return team

    def get_all(self) -> List[Team]:
        return self.db.query(Team).order_by(Team.name).all()
