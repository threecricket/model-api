import uuid
from dataclasses import dataclass
from datetime import date, datetime


def _parse_datetime(value) -> datetime | None:
    """Coerce a filter value (scalar or single-element list) into a datetime.

    Filter values arrive as lists from the ingestion gateway (e.g. ["2024-06-27"])
    but may also be passed as scalars. ISO date/datetime strings are parsed so the
    value can be compared against the timestamp columns in SQL.
    """
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        if not value:
            return None
        value = value[0]
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


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
        format_values = (
            tuple(sorted(set(str(value).lower() for value in raw_format))) if raw_format else None
        )

        raw_match_ids = filters.get("match_ids")
        match_ids = tuple(uuid.UUID(str(value)) for value in raw_match_ids) if raw_match_ids else None

        raw_innings = filters.get("innings")
        innings = tuple(int(value) for value in raw_innings) if raw_innings else None

        return cls(
            format=format_values,
            start_date=_parse_datetime(filters.get("start_date")),
            end_date=_parse_datetime(filters.get("end_date")),
            match_ids=match_ids,
            innings=innings,
        )
