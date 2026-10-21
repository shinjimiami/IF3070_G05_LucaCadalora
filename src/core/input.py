"""Shared validated problem loader for CLI and experiments."""
import json
import math
from pathlib import Path
from src.models.ship import Ship
from src.models.vehicle import Vehicle


def load_problem(path):
    with Path(path).open(encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, dict) or not isinstance(data.get("vehicles"), list):
        raise ValueError("Input requires vehicles and ship or ships")
    if "ships" in data and "ship" in data:
        raise ValueError("Specify ship or ships, not both")
    fleet = data.get("ships", [data.get("ship")])
    if not isinstance(fleet, list) or not fleet or any(not isinstance(item, dict) for item in fleet):
        raise ValueError("At least one ship object is required")
    if "ships" in data and any(not isinstance(item.get("id"), str) or not item["id"].strip() for item in fleet):
        raise ValueError("Fleet ships require nonempty string ids")
    # Validasi sebelum from_dict agar angka pecahan tidak diam-diam dibulatkan oleh core.
    for item in [*fleet, *data["vehicles"]]:
        if not isinstance(item, dict):
            raise ValueError("Setiap kendaraan harus berupa object")
        for key, value in item.items():
            if key == "id":
                continue
            if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
                raise ValueError(f"{key} harus berupa angka finite")
        for key in ("width", "length"):
            if type(item.get(key)) is not int or item[key] <= 0:
                raise ValueError(f"{key} harus integer positif")
    ships = tuple(Ship.from_dict(item) for item in fleet)
    if len({ship.id for ship in ships}) != len(ships):
        raise ValueError("Ship ids must be unique")
    vehicles = [Vehicle.from_dict(v) for v in data["vehicles"]]
    if not vehicles:
        raise ValueError("Minimal satu kendaraan diperlukan")
    if len({v.id for v in vehicles}) != len(vehicles):
        raise ValueError("ID kendaraan harus unik")
    return ships, vehicles
