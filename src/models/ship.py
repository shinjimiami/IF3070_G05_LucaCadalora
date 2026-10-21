from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Ship:
    width: int
    length: int
    max_capacity: float
    id: str = "ship-1"

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Ship id must be a nonempty string")
        if self.width <= 0 or self.length <= 0:
            raise ValueError("Ship dimensions must be positive")
        if self.max_capacity < 0:
            raise ValueError("Ship capacity cannot be negative")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Ship":
        return cls(
            id=data.get("id", "ship-1"),
            width=int(data["width"]),
            length=int(data["length"]),
            max_capacity=float(data.get("max_capacity", data.get("maxCapacity"))),
        )

    def to_dict(self) -> dict[str, str | int | float]:
        return {
            "id": self.id,
            "width": self.width,
            "length": self.length,
            "maxCapacity": self.max_capacity,
        }
