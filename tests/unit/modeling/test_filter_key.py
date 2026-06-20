from contexts.modeling.domain.models.filter_key import FilterKey


class TestFilterKey:
    def test_empty_filters_returns_default(self):
        assert FilterKey.from_filters({}).value == "default"
        assert FilterKey.from_filters(None).value == "default"

    def test_single_filter(self):
        key = FilterKey.from_filters({"format": ["t20"]})
        assert key.value == "format:t20"

    def test_multiple_filters_sorted_by_key(self):
        key = FilterKey.from_filters(
            {"start_date": "2020-01-01", "format": ["odi"]}
        )
        assert key.value == "format:odi|start_date:2020-01-01"

    def test_list_values_sorted_and_deduped(self):
        key_a = FilterKey.from_filters({"format": ["t20", "t20"]})
        key_b = FilterKey.from_filters({"format": ["t20"]})
        assert key_a.value == key_b.value == "format:t20"

    def test_list_values_lexicographically_sorted(self):
        key = FilterKey.from_filters({"format": ["odi", "t20"]})
        assert key.value == "format:odi,t20"

    def test_scalar_value(self):
        key = FilterKey.from_filters({"start_date": "2020-01-01"})
        assert key.value == "start_date:2020-01-01"
