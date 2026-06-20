from dataclasses import dataclass


@dataclass(frozen=True)
class FilterKey:
    value: str

    @staticmethod
    def from_filters(filters: dict | None) -> "FilterKey":
        if not filters:
            return FilterKey("default")

        parts: list[str] = []
        for key in sorted(filters):
            value = filters[key]
            if isinstance(value, list):
                normalized = ",".join(sorted(set(str(v) for v in value)))
            else:
                normalized = str(value)
            parts.append(f"{key}:{normalized}")

        return FilterKey("|".join(parts))
