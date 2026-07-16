from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.match import Match, MatchStatus


class MatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, match_id: int) -> Optional[Match]:
        return self.db.query(Match).filter(Match.id == match_id).first()

    def get_by_flashscore_id(self, flashscore_id: str) -> Optional[Match]:
        return (
            self.db.query(Match)
            .filter(Match.flashscore_id == flashscore_id)
            .first()
        )

    def get_matches(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        group: Optional[str] = None,
        status: Optional[list] = None,
    ) -> List[Match]:
        query = self.db.query(Match)

        if date_from:
            query = query.filter(Match.match_date >= date_from)
        if date_to:
            query = query.filter(Match.match_date <= date_to)
        if group:
            query = query.filter(Match.group_letter == group.upper())
        if status:
            query = query.filter(Match.status.in_(status))

        return query.order_by(Match.match_date).all()

    def get_finished_matches(self) -> List[Match]:
        """Получить завершённые матчи (для обогащения статистикой)."""
        return (
            self.db.query(Match)
            .filter(Match.status == MatchStatus.FINISHED)
            .order_by(Match.match_date)
            .all()
        )

    def count_remaining(self, group: Optional[str] = None) -> int:
        """
        Считает количество "оставшихся" матчей — со статусом
        scheduled или live — опционально в рамках одной группы.
        """
        query = self.db.query(Match).filter(
            Match.status.in_([MatchStatus.SCHEDULED, MatchStatus.LIVE])
        )
        if group:
            query = query.filter(Match.group_letter == group.upper())
        return query.count()

    def upsert(self, flashscore_id: str, data: dict) -> Match:
        """Создать или обновить матч по flashscore_id."""
        match = self.get_by_flashscore_id(flashscore_id)
        if match is None:
            match = Match(flashscore_id=flashscore_id)
            self.db.add(match)

        for key, value in data.items():
            if hasattr(match, key):
                setattr(match, key, value)

        self.db.flush()
        return match

    def update_stats(self, match_id: int, stats: dict) -> Optional[Match]:
        """Обновить JSONB-статистику матча."""
        match = self.get_by_id(match_id)
        if match:
            match.stats = stats
            self.db.flush()
        return match