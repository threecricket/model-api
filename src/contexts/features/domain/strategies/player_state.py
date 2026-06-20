from contexts.features.domain.models.delivery_context import DeliveryContext
from contexts.features.domain.models.feature import FeatureStrategy


class StrikerCurrentRunsStrategy:
    @property
    def name(self) -> str:
        return "striker_current_runs"

    def compute(self, context: DeliveryContext) -> float:
        return float(context.batter_runs)


class StrikerCurrentBallsFacedStrategy:
    @property
    def name(self) -> str:
        return "striker_current_balls_faced"

    def compute(self, context: DeliveryContext) -> float:
        return float(context.batter_balls)


class BowlerCurrentRunsStrategy:
    @property
    def name(self) -> str:
        return "bowler_current_runs"

    def compute(self, context: DeliveryContext) -> float:
        return float(context.bowler_runs)


class BowlerCurrentBallsBowledStrategy:
    @property
    def name(self) -> str:
        return "bowler_current_balls_bowled"

    def compute(self, context: DeliveryContext) -> float:
        return float(context.bowler_balls)


class BowlerCurrentWicketsStrategy:
    @property
    def name(self) -> str:
        return "bowler_current_wickets"

    def compute(self, context: DeliveryContext) -> float:
        return float(context.bowler_wickets)


PLAYER_STATE_STRATEGIES: list[FeatureStrategy] = [
    StrikerCurrentRunsStrategy(),
    StrikerCurrentBallsFacedStrategy(),
    BowlerCurrentRunsStrategy(),
    BowlerCurrentBallsBowledStrategy(),
    BowlerCurrentWicketsStrategy(),
]
