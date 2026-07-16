from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from ..models.standing import Standing


class StandingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Standing]:
        """Все строки таблицы, сгруппированные группой и позицией."""
        return (
            self.db.query(Standing)
            .order_by(Standing.group_name, Standing.position)
            .all()
        )

    def get_by_group(self, group_name: str) -> List[Standing]:
        return (
            self.db.query(Standing)
            .filter(Standing.group_name == group_name)
            .order_by(Standing.position)
            .all()
        )

    def get_all_grouped(self) -> List[Dict]:
        """
        Возвращает список групп с их командами, в порядке имени группы.
        Формат: [{"group": "Группа A", "teams": [Standing, ...]}, ...]
        Используется страницей /standings.
        """
        rows = self.get_all()
        grouped: Dict[str, List[Standing]] = {}
        for row in rows:
            grouped.setdefault(row.group_name, []).append(row)

        return [
            {"group": group_name, "teams": teams}
            for group_name, teams in sorted(grouped.items())
        ]

    def replace_all(self, entries: List[dict]) -> int:
        """
        Полностью заменяет таблицу: удаляет все старые строки и вставляет
        новые. Таблица championat.com пересчитывается целиком при каждом
        обновлении (позиции команд меняются местами между турами) — нет
        смысла в построчном upsert, это просто снимок текущего состояния.
        Возвращает количество вставленных строк.
        """
        self.db.query(Standing).delete()
        self.db.flush()

        for entry in entries:
            self.db.add(Standing(**entry))

        self.db.flush()
        return len(entries)