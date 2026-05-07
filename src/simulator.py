from src.models import Graph, Drone
from src.pathfinder import Pathfinder
from typing import List


class Simulator:
    def __init__(self, graph: Graph, drones: List[Drone]) -> None:
        self.graph = graph
        self.drones = drones
        self.turns: List[List[str]] = []

    def run(self) -> None:
        self._assign_paths()
        while not self._all_delivered():
            turn_output = self._process_turn()
            if turn_output:
                self.turns.append(turn_output)

    def _assign_paths(self) -> None:
        path = Pathfinder(self.graph)
        for drone in self.drones:
            drone.path = path.bfs()
            drone.in_transit = True
            drone.current_zone = self.graph.start_zone

    def _process_turn(self) -> List[str]:
        turn_log: List[str] = []

        for drone in self.drones:
            if drone.delivered:
                continue

            next_zone = drone.get_next_zone()

            if next_zone is None:
                continue

            if not next_zone.has_capacity():
                continue

            drone.move_to_next()

            if drone.current_zone is None:
                continue

            turn_log.append(f"D{drone.drone_id}-{drone.current_zone.name}")

            if drone.current_zone == self.graph.end_zone:
                drone.delivered = True
                drone.current_zone.remove_drone(drone.drone_id)

        return turn_log

    def _all_delivered(self) -> bool:
        for drone in self.drones:
            if not drone.delivered:
                return False
        return True

    def display_results(self) -> None:
        for turn_moves in self.turns:
            print(" ".join(turn_moves))
