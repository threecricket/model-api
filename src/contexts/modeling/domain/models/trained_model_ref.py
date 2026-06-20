from dataclasses import dataclass

from contexts.modeling.domain.models.filter_key import FilterKey


@dataclass(frozen=True)
class TrainedModelRef:
    model_name: str
    filter_key: FilterKey
