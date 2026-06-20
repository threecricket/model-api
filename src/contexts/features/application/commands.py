import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TrainingFilter:
    format: tuple[str, ...] | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    match_ids: tuple[uuid.UUID, ...] | None = None
    innings: tuple[int, ...] | None = None

    @classmethod
    def from_dict(cls, filters: dict | None) -> "TrainingFilter":
        if not filters:
            return cls()

        raw_format = filters.get("format")
        format_values = tuple(sorted(set(raw_format))) if raw_format else None

        raw_match_ids = filters.get("match_ids")
        match_ids = tuple(uuid.UUID(str(value)) for value in raw_match_ids) if raw_match_ids else None

        raw_innings = filters.get("innings")
        innings = tuple(int(value) for value in raw_innings) if raw_innings else None

        return cls(
            format=format_values,
            start_date=filters.get("start_date"),
            end_date=filters.get("end_date"),
            match_ids=match_ids,
            innings=innings,
        )
