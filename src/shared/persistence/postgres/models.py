import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class MatchFormat(str, enum.Enum):
    TEST = "test"
    ODI = "odi"
    T20 = "t20"


class ResultType(str, enum.Enum):
    WON = "won"
    LOST = "lost"
    TIE = "tie"
    NO_RESULT = "no_result"


class WicketType(str, enum.Enum):
    BOWLED = "bowled"
    CAUGHT = "caught"
    LBW = "lbw"
    STUMP = "stump"
    RUN_OUT = "run_out"
    HIT_WICKET = "hit_wicket"
    OBSTRUCTING = "obstructing"
    OTHER = "other"


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    venue_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    team1_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    team2_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    result_type: Mapped[ResultType] = mapped_column(
        Enum(ResultType, name="result_type", create_type=False),
        nullable=False,
    )
    subject_team_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    format: Mapped[MatchFormat] = mapped_column(
        Enum(MatchFormat, name="match_format", create_type=False),
        nullable=False,
    )


class Inning(Base):
    __tablename__ = "innings"

    match_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("matches.id", ondelete="CASCADE"),
        primary_key=True,
    )
    inning_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    runs: Mapped[int] = mapped_column(Integer, nullable=False)
    wickets: Mapped[int] = mapped_column(Integer, nullable=False)
    overs: Mapped[int] = mapped_column(Integer, nullable=False)
    balls: Mapped[int] = mapped_column(Integer, nullable=False)
    target: Mapped[int | None] = mapped_column(Integer, nullable=True)
    batting_team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    bowling_team_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)


class Ball(Base):
    __tablename__ = "balls"

    match_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("matches.id", ondelete="CASCADE"),
        primary_key=True,
    )
    inning_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    delivery_sequence: Mapped[int] = mapped_column(Integer, primary_key=True)
    ball_number: Mapped[int] = mapped_column(Integer, nullable=False)
    runs: Mapped[int] = mapped_column(Integer, nullable=False)
    wickets: Mapped[int] = mapped_column(Integer, nullable=False)
    batter_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    batter_runs: Mapped[int] = mapped_column(Integer, nullable=False)
    batter_balls: Mapped[int] = mapped_column(Integer, nullable=False)
    bowler_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    bowler_runs: Mapped[int] = mapped_column(Integer, nullable=False)
    bowler_balls: Mapped[int] = mapped_column(Integer, nullable=False)
    bowler_wickets: Mapped[int] = mapped_column(Integer, nullable=False)
    non_striker_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    non_striker_runs: Mapped[int] = mapped_column(Integer, nullable=False)
    non_striker_balls: Mapped[int] = mapped_column(Integer, nullable=False)
    result_runs: Mapped[int] = mapped_column(Integer, nullable=False)
    result_out: Mapped[int] = mapped_column(Integer, nullable=False)
    result_extras: Mapped[int] = mapped_column(Integer, nullable=False)
    result_wide: Mapped[int] = mapped_column(Integer, nullable=False)
    result_no_ball: Mapped[int] = mapped_column(Integer, nullable=False)
    player_out_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    wicket_type: Mapped[WicketType | None] = mapped_column(
        Enum(WicketType, name="wicket_type", create_type=False),
        nullable=True,
    )
