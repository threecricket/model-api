from contexts.features.domain.models.delivery_context import (
    FORMAT_MAX_LEGAL_BALLS,
    DeliveryContext,
)
from contexts.features.domain.models.feature import FeatureStrategy


class CurrentInningsRunsStrategy:
    @property
    def name(self) -> str:
        return "current_innings_runs"

    def compute(self, context: DeliveryContext) -> float:
        return float(context.runs)


class CurrentInningsWicketsStrategy:
    @property
    def name(self) -> str:
        return "current_innings_wickets"

    def compute(self, context: DeliveryContext) -> float:
        return float(context.wickets)


class CurrentInningsLegalBallNoStrategy:
    @property
    def name(self) -> str:
        return "current_innings_legal_ball_no"

    def compute(self, context: DeliveryContext) -> float:
        return float(context.ball_number)


class CurrentInningsLegalBallsRemainingStrategy:
    @property
    def name(self) -> str:
        return "current_innings_legal_balls_remaining"

    def compute(self, context: DeliveryContext) -> float:
        max_balls = FORMAT_MAX_LEGAL_BALLS.get(context.format)
        if max_balls is None:
            return 0.0
        return float(max(0, max_balls - context.ball_number + 1))


class CurrentInningsTargetStrategy:
    @property
    def name(self) -> str:
        return "current_innings_target"

    def compute(self, context: DeliveryContext) -> float:
        return float(context.target or 0)


class CurrentInningsRunsRequiredStrategy:
    @property
    def name(self) -> str:
        return "current_innings_runs_required"

    def compute(self, context: DeliveryContext) -> float:
        if context.target is None:
            return 0.0
        return float(max(0, context.target - context.runs))


INNINGS_STATE_STRATEGIES: list[FeatureStrategy] = [
    CurrentInningsRunsStrategy(),
    CurrentInningsWicketsStrategy(),
    CurrentInningsLegalBallNoStrategy(),
    CurrentInningsLegalBallsRemainingStrategy(),
    CurrentInningsTargetStrategy(),
    CurrentInningsRunsRequiredStrategy(),
]
