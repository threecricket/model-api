import uuid

import pytest

from contexts.features.domain.models.delivery_context import (
    DeliveryContext,
    MatchFormat,
    ResultType,
)


@pytest.fixture
def team_a() -> uuid.UUID:
    return uuid.UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def team_b() -> uuid.UUID:
    return uuid.UUID("22222222-2222-2222-2222-222222222222")


@pytest.fixture
def t20_chase_context(team_a: uuid.UUID, team_b: uuid.UUID) -> DeliveryContext:
    """Second innings T20 chase: 45/1 off 30 balls, target 160."""
    return DeliveryContext(
        match_id=uuid.uuid4(),
        inning_number=2,
        delivery_sequence=30,
        ball_number=30,
        runs=45,
        wickets=1,
        batter_runs=22,
        batter_balls=18,
        bowler_runs=28,
        bowler_balls=30,
        bowler_wickets=1,
        target=160,
        batting_team_id=team_a,
        subject_team_id=team_a,
        result_type=ResultType.WON,
        format=MatchFormat.T20,
    )


@pytest.fixture
def first_innings_context(team_a: uuid.UUID, team_b: uuid.UUID) -> DeliveryContext:
    """First innings with no target set."""
    return DeliveryContext(
        match_id=uuid.uuid4(),
        inning_number=1,
        delivery_sequence=50,
        ball_number=50,
        runs=62,
        wickets=2,
        batter_runs=30,
        batter_balls=35,
        bowler_runs=55,
        bowler_balls=50,
        bowler_wickets=2,
        target=None,
        batting_team_id=team_a,
        subject_team_id=team_b,
        result_type=ResultType.LOST,
        format=MatchFormat.ODI,
    )


@pytest.fixture
def test_format_context(team_a: uuid.UUID) -> DeliveryContext:
    """Test match — no fixed ball limit."""
    return DeliveryContext(
        match_id=uuid.uuid4(),
        inning_number=1,
        delivery_sequence=100,
        ball_number=100,
        runs=250,
        wickets=3,
        batter_runs=80,
        batter_balls=120,
        bowler_runs=200,
        bowler_balls=100,
        bowler_wickets=2,
        target=None,
        batting_team_id=team_a,
        subject_team_id=team_a,
        result_type=ResultType.WON,
        format=MatchFormat.TEST,
    )
