from dataclasses import dataclass
from typing import Protocol

from contexts.features.domain.models.delivery_context import DeliveryContext


@dataclass(frozen=True)
class Feature:
    name: str
    dependencies: tuple[str, ...] = ()


class FeatureStrategy(Protocol):
    @property
    def name(self) -> str: ...

    def compute(self, context: DeliveryContext) -> float: ...
