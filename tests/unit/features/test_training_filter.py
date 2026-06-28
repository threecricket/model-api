import uuid
from datetime import datetime

from contexts.features.application.commands import TrainingFilter


class TestTrainingFilterFromDict:
    def test_empty_filters(self):
        assert TrainingFilter.from_dict(None) == TrainingFilter()
        assert TrainingFilter.from_dict({}) == TrainingFilter()

    def test_parses_format_and_innings(self):
        training_filter = TrainingFilter.from_dict(
            {"format": ["T20"], "innings": ["1", "2"]}
        )

        assert training_filter.format == ("t20",)
        assert training_filter.innings == (1, 2)

    def test_parses_start_date_from_single_element_list(self):
        training_filter = TrainingFilter.from_dict({"start_date": ["2024-06-27"]})

        assert training_filter.start_date == datetime(2024, 6, 27)

    def test_parses_start_date_from_scalar(self):
        training_filter = TrainingFilter.from_dict({"start_date": "2024-06-27"})

        assert training_filter.start_date == datetime(2024, 6, 27)

    def test_parses_end_date(self):
        training_filter = TrainingFilter.from_dict({"end_date": ["2026-01-01"]})

        assert training_filter.end_date == datetime(2026, 1, 1)

    def test_ignores_empty_date_list(self):
        training_filter = TrainingFilter.from_dict({"start_date": []})

        assert training_filter.start_date is None

    def test_parses_match_ids(self):
        match_id = uuid.uuid4()
        training_filter = TrainingFilter.from_dict({"match_ids": [str(match_id)]})

        assert training_filter.match_ids == (match_id,)
