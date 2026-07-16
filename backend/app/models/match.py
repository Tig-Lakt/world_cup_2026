import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from ..core.database import Base


class MatchStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    LIVE      = "live"
    FINISHED  = "finished"
    POSTPONED = "postponed"


class Match(Base):
    __tablename__ = "matches"

    id             = Column(Integer, primary_key=True, index=True)
    flashscore_id  = Column(String(20), unique=True, nullable=False)
    match_url      = Column(String(500), nullable=True)

    home_team_id   = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id   = Column(Integer, ForeignKey("teams.id"), nullable=False)

    # nullable=True: Flashscore иногда отдаёт время в формате, который
    # _parse_time не распознаёт (см. sync.py) — лучше сохранить матч
    # без даты, чем потерять его целиком из-за IntegrityError.
    match_date     = Column(DateTime(timezone=True), nullable=True)
    status         = Column(Enum(MatchStatus), default=MatchStatus.SCHEDULED, nullable=False)

    home_score     = Column(Integer, nullable=True)
    away_score     = Column(Integer, nullable=True)

    stage          = Column(String(50),  nullable=True)
    group_letter   = Column(String(1),   nullable=True)

    venue          = Column(String(200), nullable=True)
    city           = Column(String(100), nullable=True)

    stats          = Column(JSONB, nullable=True)

    created_at     = Column(DateTime(timezone=True), server_default=func.now())
    updated_at     = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return (
            f"<Match(id={self.id}, "
            f"home_team_id={self.home_team_id}, away_team_id={self.away_team_id}, "
            f"score={self.home_score}:{self.away_score}, status='{self.status}')>"
        )
