from contexts.features.domain.models.delivery_context import DeliveryContext, ResultType
from contexts.features.domain.models.feature import FeatureStrategy


class BattingTeamWonStrategy:
    @property
    def name(self) -> str:
        return "batting_team_won"

    def compute(self, context: DeliveryContext) -> float:
        if context.result_type != ResultType.WON:
            return 0.0
        if context.subject_team_id is None:
            return 0.0
        if context.batting_team_id != context.subject_team_id:
            return 0.0
        return 1.0


OUTCOME_STRATEGIES: list[FeatureStrategy] = [
    BattingTeamWonStrategy(),
]
