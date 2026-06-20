from contexts.features.domain.strategies.player_state import (
    BowlerCurrentBallsBowledStrategy,
    BowlerCurrentRunsStrategy,
    BowlerCurrentWicketsStrategy,
    StrikerCurrentBallsFacedStrategy,
    StrikerCurrentRunsStrategy,
)


class TestPlayerStateStrategies:
    def test_striker_current_runs(self, t20_chase_context):
        assert StrikerCurrentRunsStrategy().compute(t20_chase_context) == 22.0

    def test_striker_current_balls_faced(self, t20_chase_context):
        assert StrikerCurrentBallsFacedStrategy().compute(t20_chase_context) == 18.0

    def test_bowler_current_runs(self, t20_chase_context):
        assert BowlerCurrentRunsStrategy().compute(t20_chase_context) == 28.0

    def test_bowler_current_balls_bowled(self, t20_chase_context):
        assert BowlerCurrentBallsBowledStrategy().compute(t20_chase_context) == 30.0

    def test_bowler_current_wickets(self, t20_chase_context):
        assert BowlerCurrentWicketsStrategy().compute(t20_chase_context) == 1.0
