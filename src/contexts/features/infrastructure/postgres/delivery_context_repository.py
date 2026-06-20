from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from contexts.features.application.commands import TrainingFilter
from contexts.features.domain.models.delivery_context import (
    DeliveryContext,
    MatchFormat,
    ResultType,
)
from shared.persistence.postgres.models import Ball, Inning, Match, MatchFormat as DbMatchFormat


class DeliveryContextRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_filter(self, training_filter: TrainingFilter) -> list[DeliveryContext]:
        stmt = self._build_query(training_filter)
        rows = self._session.execute(stmt).all()
        return [self._to_delivery_context(row) for row in rows]

    def _build_query(self, training_filter: TrainingFilter) -> Select:
        stmt = (
            select(
                Ball.match_id,
                Ball.inning_number,
                Ball.delivery_sequence,
                Ball.ball_number,
                Ball.runs,
                Ball.wickets,
                Ball.batter_runs,
                Ball.batter_balls,
                Ball.bowler_runs,
                Ball.bowler_balls,
                Ball.bowler_wickets,
                Inning.target,
                Inning.batting_team_id,
                Match.subject_team_id,
                Match.result_type,
                Match.format,
            )
            .join(
                Inning,
                (Ball.match_id == Inning.match_id) & (Ball.inning_number == Inning.inning_number),
            )
            .join(Match, Ball.match_id == Match.id)
            .order_by(Ball.match_id, Ball.inning_number, Ball.delivery_sequence)
        )

        if training_filter.format:
            db_formats = [DbMatchFormat(value) for value in training_filter.format]
            stmt = stmt.where(Match.format.in_(db_formats))

        if training_filter.start_date is not None:
            stmt = stmt.where(Match.start_date >= training_filter.start_date)

        if training_filter.end_date is not None:
            stmt = stmt.where(Match.start_date <= training_filter.end_date)

        if training_filter.match_ids:
            stmt = stmt.where(Match.id.in_(training_filter.match_ids))

        return stmt

    @staticmethod
    def _to_delivery_context(row) -> DeliveryContext:
        return DeliveryContext(
            match_id=row.match_id,
            inning_number=row.inning_number,
            delivery_sequence=row.delivery_sequence,
            ball_number=row.ball_number,
            runs=row.runs,
            wickets=row.wickets,
            batter_runs=row.batter_runs,
            batter_balls=row.batter_balls,
            bowler_runs=row.bowler_runs,
            bowler_balls=row.bowler_balls,
            bowler_wickets=row.bowler_wickets,
            target=row.target,
            batting_team_id=row.batting_team_id,
            subject_team_id=row.subject_team_id,
            result_type=ResultType(row.result_type.value),
            format=MatchFormat(row.format.value),
        )
