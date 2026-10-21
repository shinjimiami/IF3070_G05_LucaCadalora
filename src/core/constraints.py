from itertools import combinations

from src.models.state import Placement, State


def is_inside_boundary(state: State) -> bool:
    ships = {ship.id: ship for ship in state.ships}
    for placement in state.inside_placements:
        if placement.ship_id not in ships:
            return False
        ship = ships[placement.ship_id]
        if placement.x is None or placement.y is None:
            return False
        if placement.x < 0 or placement.y < 0:
            return False
        if placement.x + placement.placed_width > ship.width:
            return False
        if placement.y + placement.placed_length > ship.length:
            return False
    return True


def placements_overlap(first: Placement, second: Placement) -> bool:
    if not first.inside or not second.inside or first.ship_id != second.ship_id:
        return False
    if first.x is None or first.y is None or second.x is None or second.y is None:
        return False
    return (
        first.x < second.x + second.placed_width
        and first.x + first.placed_width > second.x
        and first.y < second.y + second.placed_length
        and first.y + first.placed_length > second.y
    )


def has_overlap(state: State) -> bool:
    return any(
        placements_overlap(first, second)
        for first, second in combinations(state.inside_placements, 2)
    )


def within_capacity(state: State) -> bool:
    return all(state.weight_on(ship.id) <= ship.max_capacity for ship in state.ships)


def is_valid_state(state: State) -> bool:
    ids = [p.vehicle.id for p in state.placements]
    ship_ids = {ship.id for ship in state.ships}
    assignments_valid = all(
        p.ship_id in ship_ids if p.inside else p.ship_id is None
        for p in state.placements
    )
    return (len(ids) == len(set(ids)) and assignments_valid
            and is_inside_boundary(state) and not has_overlap(state) and within_capacity(state))
