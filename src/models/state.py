from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Iterable

from .ship import Ship
from .vehicle import Vehicle


class Orientation(str, Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

    def rotated(self) -> "Orientation":
        if self is Orientation.HORIZONTAL:
            return Orientation.VERTICAL
        return Orientation.HORIZONTAL


@dataclass(frozen=True, slots=True)
class Placement:
    vehicle: Vehicle
    inside: bool = False
    x: int | None = None
    y: int | None = None
    orientation: Orientation = Orientation.HORIZONTAL
    ship_id: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.orientation, str):
            object.__setattr__(self, "orientation", Orientation(self.orientation.lower()))
        if self.inside and (self.x is None or self.y is None):
            raise ValueError("Inside placement requires coordinates")

    @property
    def placed_width(self) -> int:
        if self.orientation is Orientation.HORIZONTAL:
            return self.vehicle.width
        return self.vehicle.length

    @property
    def placed_length(self) -> int:
        if self.orientation is Orientation.HORIZONTAL:
            return self.vehicle.length
        return self.vehicle.width

    @classmethod
    def outside(cls, vehicle: Vehicle) -> "Placement":
        return cls(vehicle=vehicle)

    def to_dict(self) -> dict[str, Any]:
        return {
            "vehicle": self.vehicle.to_dict(),
            "inside": self.inside,
            "ship_id": self.ship_id,
            "x": self.x,
            "y": self.y,
            "orientation": self.orientation.value,
        }


@dataclass(slots=True)
class State:
    ship: Ship | None = None
    placements: list[Placement] = field(default_factory=list)
    objective_value: float = 0.0
    total_weight: float = 0.0

    ships: tuple[Ship, ...] = ()

    def __post_init__(self) -> None:
        self.ships = tuple(self.ships) or ((self.ship,) if self.ship is not None else ())
        if not self.ships:
            raise ValueError("At least one ship is required")
        if len({s.id for s in self.ships}) != len(self.ships):
            raise ValueError("Ship ids must be unique")
        self.ship = self.ships[0] if len(self.ships) == 1 else None
        # Normalize legacy single-ship placements at the model boundary.
        self.placements = [
            replace(p, ship_id=self.ship.id)
            if p.inside and p.ship_id is None and self.ship is not None else p
            for p in self.placements
        ]
        ship_ids = {ship.id for ship in self.ships}
        if any(
            (p.inside and p.ship_id not in ship_ids)
            or (not p.inside and p.ship_id is not None)
            for p in self.placements
        ):
            raise ValueError("Invalid ship assignment")
        ids = [placement.vehicle.id for placement in self.placements]
        if len(ids) != len(set(ids)):
            raise ValueError("Vehicle ids must be unique within a state")

    def placements_on(self, ship_id: str) -> list[Placement]:
        return [p for p in self.inside_placements if p.ship_id == ship_id]

    def weight_on(self, ship_id: str) -> float:
        return sum(p.vehicle.weight for p in self.placements_on(ship_id))

    @property
    def inside_placements(self) -> list[Placement]:
        return [placement for placement in self.placements if placement.inside]

    @property
    def outside_placements(self) -> list[Placement]:
        return [placement for placement in self.placements if not placement.inside]

    @property
    def vehicles(self) -> list[Vehicle]:
        return [placement.vehicle for placement in self.placements]

    def replace_placement(self, index: int, placement: Placement) -> "State":
        placements = self.placements.copy()
        placements[index] = placement
        return replace(self, placements=placements)

    def replace_placements(self, placements: Iterable[Placement]) -> "State":
        return replace(self, placements=list(placements))

    def to_dict(self) -> dict[str, Any]:
        return {
            **({"ship": self.ship.to_dict()} if self.ship is not None else {}),
            "ships": [ship.to_dict() for ship in self.ships],
            "placements": [placement.to_dict() for placement in self.placements],
            "objectiveValue": self.objective_value,
            "totalWeight": self.total_weight,
        }
