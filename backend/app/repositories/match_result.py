from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.match_result import MatchResult


class MatchResultRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, result_id: int) -> Optional[MatchResult]:
        return self.db.query(MatchResult).filter(MatchResult.id == result_id).first()

    def get_by_championat_id(self, championat_id: str) -> Optional[MatchResult]:
        return (
            self.db.query(MatchResult)
            .filter(MatchResult.championat_id == championat_id)
            .first()
        )

    def get_all(self, group_name: Optional[str] = None) -> List[MatchResult]:
        """Все результаты, свежие сверху (по убыванию даты), опционально по группе."""
        query = self.db.query(MatchResult)
        if group_name:
            query = query.filter(MatchResult.group_name == group_name)
        return query.order_by(MatchResult.match_date.desc()).all()

    def upsert(self, championat_id: str, data: dict) -> MatchResult:
        """Создать или обновить результат матча по championat_id."""
        result = self.get_by_championat_id(championat_id)
        if result is None:
            result = MatchResult(championat_id=championat_id)
            self.db.add(result)

        for key, value in data.items():
            if hasattr(result, key):
                setattr(result, key, value)

        self.db.flush()
        return result

    def update_stats(self, result_id: int, stats: dict) -> Optional[MatchResult]:
        """Обновить JSONB-статистику результата."""
        result = self.get_by_id(result_id)
        if result:
            result.stats = stats
            self.db.flush()
        return result