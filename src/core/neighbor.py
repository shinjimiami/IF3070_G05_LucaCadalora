from collections.abc import Iterator
from itertools import chain

from src.core.constraints import is_valid_state
from src.core.objective import with_updated_metrics
from src.models.state import Orientation, Placement, State


def _find_index(state: State, vehicle_id: str) -> int:
    for index, placement in enumerate(state.placements):
        if placement.vehicle.id == vehicle_id:
            return index
    raise ValueError(f"Vehicle not found: {vehicle_id}")


def move_vehicle(
    state: State,
    vehicle_id: str,
    x: int,
    y: int,
    orientation: Orientation | str | None = None,
    objective_mode: str = "shipping_fee",
    ship_id: str | None = None,
) -> State | None:
    index = _find_index(state, vehicle_id)
    current = state.placements[index]
    target = ship_id or current.ship_id or state.ships[0].id
    if target not in {ship.id for ship in state.ships}:
        raise ValueError("Unknown ship id")
    placement = Placement(
        vehicle=current.vehicle,
        inside=True,
        ship_id=target,
        x=x,
        y=y,
        orientation=orientation or current.orientation,
    )
    candidate = state.replace_placement(index, placement)
    if not is_valid_state(candidate):
        return None
    return with_updated_metrics(candidate, objective_mode)


def rotate_vehicle(
    state: State,
    vehicle_id: str,
    objective_mode: str = "shipping_fee",
) -> State | None:
    index = _find_index(state, vehicle_id)
    current = state.placements[index]
    if not current.inside or current.x is None or current.y is None:
        return None
    placement = Placement(
        vehicle=current.vehicle,
        inside=True,
        x=current.x,
        y=current.y,
        orientation=current.orientation.rotated(),
        ship_id=current.ship_id,
    )
    candidate = state.replace_placement(index, placement)
    if not is_valid_state(candidate):
        return None
    return with_updated_metrics(candidate, objective_mode)


def swap_vehicles(
    state: State,
    first_vehicle_id: str,
    second_vehicle_id: str,
    objective_mode: str = "shipping_fee",
) -> State | None:
    first_index = _find_index(state, first_vehicle_id)
    second_index = _find_index(state, second_vehicle_id)
    if first_index == second_index:
        return None

    first = state.placements[first_index]
    second = state.placements[second_index]
    if not first.inside and not second.inside:
        return None

    placements = state.placements.copy()
    placements[first_index] = Placement(
        vehicle=first.vehicle,
        inside=second.inside,
        ship_id=second.ship_id,
        x=second.x if second.inside else None,
        y=second.y if second.inside else None,
        orientation=second.orientation,
    )
    placements[second_index] = Placement(
        vehicle=second.vehicle,
        inside=first.inside,
        ship_id=first.ship_id,
        x=first.x if first.inside else None,
        y=first.y if first.inside else None,
        orientation=first.orientation,
    )
    candidate = state.replace_placements(placements)
    if not is_valid_state(candidate):
        return None
    return with_updated_metrics(candidate, objective_mode)


def remove_vehicle(state, vehicle_id, objective_mode="shipping_fee"):
    index = _find_index(state, vehicle_id)
    if not state.placements[index].inside:
        return None
    return with_updated_metrics(state.replace_placement(index, Placement.outside(state.placements[index].vehicle)), objective_mode)


def _move_candidates(state: State, objective_mode: str) -> Iterator[State]:
    for placement in state.placements:
        for ship in state.ships:
            for orientation in Orientation:
                width = placement.vehicle.width if orientation is Orientation.HORIZONTAL else placement.vehicle.length
                length = placement.vehicle.length if orientation is Orientation.HORIZONTAL else placement.vehicle.width
                for y in range(ship.length - length + 1):
                    for x in range(ship.width - width + 1):
                        if (placement.inside and placement.ship_id == ship.id and
                            (x, y, orientation) == (placement.x, placement.y, placement.orientation)):
                            continue
                        candidate = move_vehicle(state, placement.vehicle.id, x, y, orientation, objective_mode, ship.id)
                        if candidate is not None:
                            yield candidate
        if placement.inside:
            yield remove_vehicle(state, placement.vehicle.id, objective_mode)


def random_move(state, generator, objective_mode="shipping_fee"):
    if not state.placements:
        return None
    placement = generator.choice(state.placements)
    ship = generator.choice(state.ships)
    orientation = generator.choice(list(Orientation))
    width = placement.vehicle.width if orientation is Orientation.HORIZONTAL else placement.vehicle.length
    length = placement.vehicle.length if orientation is Orientation.HORIZONTAL else placement.vehicle.width
    if width > ship.width or length > ship.length:
        return None
    return move_vehicle(state, placement.vehicle.id, generator.randrange(ship.width - width + 1),
                        generator.randrange(ship.length - length + 1), orientation, objective_mode, ship.id)


def random_removal(state, generator, objective_mode="shipping_fee"):
    if not state.inside_placements:
        return None
    return remove_vehicle(state, generator.choice(state.inside_placements).vehicle.id, objective_mode)


def _rotate_candidates(state: State, objective_mode: str) -> Iterator[State]:
    for placement in state.inside_placements:
        candidate = rotate_vehicle(state, placement.vehicle.id, objective_mode)
        if candidate is not None:
            yield candidate


def _swap_candidates(state: State, objective_mode: str) -> Iterator[State]:
    for first_index in range(len(state.placements)):
        for second_index in range(first_index + 1, len(state.placements)):
            candidate = swap_vehicles(
                state,
                state.placements[first_index].vehicle.id,
                state.placements[second_index].vehicle.id,
                objective_mode,
            )
            if candidate is not None:
                yield candidate


def _state_key(state: State) -> tuple[tuple[object, ...], ...]:
    return tuple(
        (
            placement.vehicle.id,
            placement.inside,
            placement.ship_id,
            placement.x,
            placement.y,
            placement.orientation.value,
        )
        for placement in state.placements
    )


def generate_neighbors(
    state: State,
    objective_mode: str = "shipping_fee",
) -> list[State]:
    neighbors: list[State] = []
    seen: set[tuple[tuple[object, ...], ...]] = set()
    candidates = chain(
        _move_candidates(state, objective_mode),
        _rotate_candidates(state, objective_mode),
        _swap_candidates(state, objective_mode),
    )
    for candidate in candidates:
        key = _state_key(candidate)
        if key not in seen:
            seen.add(key)
            neighbors.append(candidate)
    return neighbors
