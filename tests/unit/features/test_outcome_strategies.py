import uuid

from contexts.features.domain.models.delivery_context import DeliveryContext, MatchFormat, ResultType
from contexts.features.domain.strategies.outcome import BattingTeamWonStrategy


class TestBattingTeamWonStrategy:
    def test_batting_team_won(self, t20_chase_context):
        assert BattingTeamWonStrategy().compute(t20_chase_context) == 1.0

    def test_losing_team_returns_zero(self, first_innings_context):
        assert BattingTeamWonStrategy().compute(first_innings_context) == 0.0

    def test_tie_returns_zero(self, team_a, team_b):
        context = DeliveryContext(
            match_id=uuid.uuid4(),
            inning_number=2,
            delivery_sequence=120,
            ball_number=120,
            runs=160,
            wickets=5,
            batter_runs=10,
            batter_balls=8,
            bowler_runs=160,
            bowler_balls=120,
            bowler_wickets=5,
            target=160,
            batting_team_id=team_a,
            subject_team_id=team_a,
            result_type=ResultType.TIE,
            format=MatchFormat.T20,
        )
        assert BattingTeamWonStrategy().compute(context) == 0.0

    def test_no_result_returns_zero(self, team_a):
        context = DeliveryContext(
            match_id=uuid.uuid4(),
            inning_number=1,
            delivery_sequence=10,
            ball_number=10,
            runs=20,
            wickets=0,
            batter_runs=15,
            batter_balls=10,
            bowler_runs=20,
            bowler_balls=10,
            bowler_wickets=0,
            target=None,
            batting_team_id=team_a,
            subject_team_id=team_a,
            result_type=ResultType.NO_RESULT,
            format=MatchFormat.T20,
        )
        assert BattingTeamWonStrategy().compute(context) == 0.0

    def test_missing_subject_team_returns_zero(self, team_a):
        context = DeliveryContext(
            match_id=uuid.uuid4(),
            inning_number=1,
            delivery_sequence=10,
            ball_number=10,
            runs=20,
            wickets=0,
            batter_runs=15,
            batter_balls=10,
            bowler_runs=20,
            bowler_balls=10,
            bowler_wickets=0,
            target=None,
            batting_team_id=team_a,
            subject_team_id=None,
            result_type=ResultType.WON,
            format=MatchFormat.T20,
        )
        assert BattingTeamWonStrategy().compute(context) == 0.0
