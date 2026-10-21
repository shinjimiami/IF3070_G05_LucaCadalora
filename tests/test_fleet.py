import contextlib
import io
import json
import random
import tempfile
import unittest
from pathlib import Path

from src.models.ship import Ship
from src.models.vehicle import Vehicle
from src.models.state import State, Placement
from src.core.constraints import is_valid_state, has_overlap, within_capacity
from src.core.initialization import create_outside_state, generate_random_state
from src.core.neighbor import move_vehicle, swap_vehicles, remove_vehicle, generate_neighbors
from src.algorithms.hill_climbing import hill_climb, VALID_VARIANTS
from src.algorithms.simulated_annealing import simulated_annealing
from src.algorithms.genetic_algorithm import genetic_algorithm
from src.main import main, load_problem
from src.visualization.export import restore_state


class FleetTest(unittest.TestCase):
    def setUp(self):
        self.ships = (Ship(2, 2, 5, "A"), Ship(2, 2, 3, "B"))
        self.vehicles = [Vehicle("one", 2, 2, 100, 5, 0), Vehicle("two", 2, 2, 60, 3, 0)]

    def test_per_ship_constraints_and_unique_assignments(self):
        a, b = self.vehicles
        state = State(ships=self.ships, placements=[Placement(a, True, 0, 0, ship_id="A"), Placement(b, True, 0, 0, ship_id="B")])
        self.assertTrue(is_valid_state(state))
        self.assertFalse(has_overlap(state))
        overloaded = State(ships=self.ships, placements=[Placement(a, True, 0, 0, ship_id="B")])
        self.assertFalse(within_capacity(overloaded))
        with self.assertRaises(ValueError):
            State(ships=self.ships, placements=[Placement(a), Placement(a)])
        with self.assertRaises(ValueError):
            State(ships=self.ships, placements=[Placement(a, True, 0, 0, ship_id="missing")])
        with self.assertRaises(ValueError):
            State(ships=(self.ships[0], self.ships[0]))
        self.assertFalse(is_valid_state(State(ships=self.ships, placements=[Placement(a, True, 1, 0, ship_id="A")])))

    def test_transfer_swap_and_removal(self):
        a, b = self.vehicles
        state = State(ships=self.ships, placements=[Placement(a, True, 0, 0, ship_id="A"), Placement(b, True, 0, 0, ship_id="B")])
        self.assertIsNone(swap_vehicles(state, "one", "two"))
        state = remove_vehicle(state, "one")
        transferred = move_vehicle(state, "two", 0, 0, ship_id="A")
        self.assertEqual(transferred.placements[1].ship_id, "A")
        self.assertTrue(is_valid_state(transferred))
        self.assertIsNone(move_vehicle(transferred, "one", 0, 0, ship_id="B"))
        equal_ships = (Ship(2, 2, 5, "A"), Ship(2, 2, 5, "B"))
        full = State(ships=equal_ships, placements=[Placement(a, True, 0, 0, ship_id="A"), Placement(b, True, 0, 0, ship_id="B")])
        swapped = swap_vehicles(full, "one", "two")
        self.assertEqual([p.ship_id for p in swapped.placements], ["B", "A"])
        self.assertTrue(is_valid_state(swapped))
        removed = remove_vehicle(full, "one")
        replacement = swap_vehicles(removed, "one", "two")
        self.assertTrue(is_valid_state(replacement))
        self.assertEqual(replacement.placements[0].ship_id, "B")
        self.assertFalse(replacement.placements[1].inside)

    def test_initialization_neighbors_and_roundtrip(self):
        large = Vehicle("large", 5, 5, 500, 1, 0)
        first = generate_random_state(self.ships, self.vehicles + [large], rng=random.Random(4))
        second = generate_random_state(self.ships, self.vehicles + [large], rng=random.Random(4))
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertFalse(first.placements[-1].inside)
        self.assertEqual(restore_state(first.to_dict()).to_dict(), first.to_dict())
        empty = create_outside_state(self.ships, self.vehicles)
        neighbors = generate_neighbors(empty)
        self.assertTrue(all(is_valid_state(n) for n in neighbors))
        self.assertEqual({n.placements[1].ship_id for n in neighbors if n.placements[1].inside}, {"A", "B"})
        legacy = {'ship': {'width':2,'length':2,'maxCapacity':5}, 'placements': [], 'objectiveValue':0, 'totalWeight':0}
        self.assertTrue(is_valid_state(restore_state(legacy)))

    def test_algorithms_known_optimum_and_reproducibility(self):
        initial = create_outside_state(self.ships, self.vehicles)
        for variant in VALID_VARIANTS:
            result = hill_climb(initial, variant=variant, max_iterations=10, max_restart=2, seed=4)
            self.assertTrue(is_valid_state(result["final_state"]))
            self.assertEqual(result["best_objective"], 160)
        for algorithm, params in [(simulated_annealing, {'max_iterations':100}), (genetic_algorithm, {'population_size':6,'generations':10})]:
            first = algorithm(initial, seed=4, **params)
            second = algorithm(initial, seed=4, **params)
            self.assertTrue(is_valid_state(first['final_state']))
            self.assertEqual(first['final_state'].to_dict(), second['final_state'].to_dict())
            self.assertEqual(first['best_objective'], 160)

    def test_fleet_cli_and_input_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            for algorithm in ('hc', 'sa', 'ga'):
                dest = Path(directory) / algorithm
                with contextlib.redirect_stdout(io.StringIO()):
                    code = main(['--input','input/multi_ship.json','--algorithm',algorithm,'--max-iterations','5','--population','4','--generations','2','--output',str(dest)])
                self.assertEqual(code, 0)
                result = json.loads((dest / 'result.json').read_text())
                self.assertEqual(len(result['final_state']['ships']),2)
                self.assertTrue(is_valid_state(restore_state(result['final_state'])))
                self.assertGreater((dest / 'final_state.png').stat().st_size, 0)
            path = Path(directory) / 'bad.json'
            for ships in [[], [{'id':'A','width':2,'length':2,'maxCapacity':3}]*2, [{'width':2,'length':2,'maxCapacity':3}]]:
                path.write_text(json.dumps({'ships':ships,'vehicles':[self.vehicles[0].to_dict()]}))
                with self.assertRaises(ValueError):
                    load_problem(path)
