import uuid
from dataclasses import dataclass
from enum import Enum


class MatchFormat(str, Enum):
    TEST = "test"
    ODI = "odi"
    T20 = "t20"


class ResultType(str, Enum):
    WON = "won"
    LOST = "lost"
    TIE = "tie"
    NO_RESULT = "no_result"


FORMAT_MAX_LEGAL_BALLS: dict[MatchFormat, int | None] = {
    MatchFormat.T20: 120,
    MatchFormat.ODI: 300,
    MatchFormat.TEST: None,
}


@dataclass(frozen=True)
class DeliveryContext:
    match_id: uuid.UUID
    inning_number: int
    delivery_sequence: int
    ball_number: int
    runs: int
    wickets: int
    batter_runs: int
    batter_balls: int
    bowler_runs: int
    bowler_balls: int
    bowler_wickets: int
    target: int | None
    batting_team_id: uuid.UUID
    subject_team_id: uuid.UUID | None
    result_type: ResultType
    format: MatchFormat
