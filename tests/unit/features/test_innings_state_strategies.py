from contexts.features.domain.strategies.innings_state import (
    CurrentInningsLegalBallNoStrategy,
    CurrentInningsLegalBallsRemainingStrategy,
    CurrentInningsRunsRequiredStrategy,
    CurrentInningsRunsStrategy,
    CurrentInningsTargetStrategy,
    CurrentInningsWicketsStrategy,
)


class TestInningsStateStrategies:
    def test_current_innings_runs(self, t20_chase_context):
        assert CurrentInningsRunsStrategy().compute(t20_chase_context) == 45.0

    def test_current_innings_wickets(self, t20_chase_context):
        assert CurrentInningsWicketsStrategy().compute(t20_chase_context) == 1.0

    def test_current_innings_legal_ball_no(self, t20_chase_context):
        assert CurrentInningsLegalBallNoStrategy().compute(t20_chase_context) == 30.0

    def test_legal_balls_remaining_t20(self, t20_chase_context):
        # 120 max - 30 + 1 = 91
        assert CurrentInningsLegalBallsRemainingStrategy().compute(t20_chase_context) == 91.0

    def test_legal_balls_remaining_odi(self, first_innings_context):
        # 300 max - 50 + 1 = 251
        assert CurrentInningsLegalBallsRemainingStrategy().compute(first_innings_context) == 251.0

    def test_legal_balls_remaining_test_is_zero(self, test_format_context):
        assert CurrentInningsLegalBallsRemainingStrategy().compute(test_format_context) == 0.0

    def test_current_innings_target_with_target(self, t20_chase_context):
        assert CurrentInningsTargetStrategy().compute(t20_chase_context) == 160.0

    def test_current_innings_target_without_target(self, first_innings_context):
        assert CurrentInningsTargetStrategy().compute(first_innings_context) == 0.0

    def test_runs_required_with_target(self, t20_chase_context):
        assert CurrentInningsRunsRequiredStrategy().compute(t20_chase_context) == 115.0

    def test_runs_required_without_target(self, first_innings_context):
        assert CurrentInningsRunsRequiredStrategy().compute(first_innings_context) == 0.0
