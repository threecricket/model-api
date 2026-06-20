import pytest
from pydantic import ValidationError

from api.schemas.predict import PredictRequest


class TestPredictRequestValidation:
    def test_accepts_filters(self):
        req = PredictRequest(
            model="batting_team_win_probability",
            filters={"format": ["t20"]},
            input={"current_innings_runs": [45.0, 120.0]},
        )
        assert req.filters == {"format": ["t20"]}
        assert req.filter_key is None

    def test_accepts_filter_key(self):
        req = PredictRequest(
            model="batting_team_win_probability",
            filter_key="format:t20",
            input={"current_innings_runs": [45.0]},
        )
        assert req.filter_key == "format:t20"

    def test_requires_filter_key_or_filters(self):
        with pytest.raises(ValidationError, match="Either filter_key or filters must be provided"):
            PredictRequest(
                model="batting_team_win_probability",
                input={"current_innings_runs": [45.0]},
            )
