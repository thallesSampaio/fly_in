from src.models import Graph, Drone, ZoneType
from src.pathfinder import Pathfinder
from typing import List


class Simulator:
    def __init__(self, graph: Graph, drones: List[Drone]) -> None:
        self.graph = graph
        self.drones = drones
        self.turns: List[List[str]] = []

    def setup(self) -> None:
        self._assign_paths()

    def step(self) -> List[str]:
        if self._all_delivered():
            return []
        turn_output = self._process_turn()
        if turn_output:
            self.turns.append(turn_output)
        return turn_output

    def run(self) -> None:
        self.setup()
        while not self._all_delivered():
            self.step()

    def _assign_paths(self) -> None:
        path = Pathfinder(self.graph)
        for drone in self.drones:
            drone.path = path.dijkstra()
            drone.current_zone = self.graph.start_zone
            if drone.current_zone is not None:
                drone.current_zone.add_drone(drone.drone_id)

    def _process_turn(self) -> List[str]:
        turn_log: List[str] = []
        moved_this_turn: set[int] = set()

        self._finish_transits(turn_log, moved_this_turn)

        for drone in self.drones:
            if (drone.delivered or drone.current_connection is not None or
                    drone.drone_id in moved_this_turn):
                continue

            next_zone = drone.get_next_zone()

            if (next_zone is None or drone.current_zone is None or
                    not next_zone.has_capacity()):
                continue

            connection = self.graph.get_connection_between(drone.current_zone,
                                                           next_zone)

            if connection is None:
                continue

            if not connection.has_capacity():
                continue

            if next_zone.zone_type == ZoneType.RESTRICTED:
                conn_name = f"{drone.current_zone.name}-{next_zone.name}"

                drone.start_transit(next_zone, connection)

                moved_this_turn.add(drone.drone_id)
                turn_log.append(f"D{drone.drone_id}-{conn_name}")

                continue

            connection.enter(drone.drone_id)
            drone.move_to_next()
            moved_this_turn.add(drone.drone_id)
            connection.leave(drone.drone_id)

            if drone.current_zone is None:
                continue

            turn_log.append(f"D{drone.drone_id}-{drone.current_zone.name}")

            if drone.current_zone == self.graph.end_zone:
                drone.delivered = True

        return turn_log

    def _all_delivered(self) -> bool:
        for drone in self.drones:
            if not drone.delivered:
                return False
        return True

    def display_results(self) -> None:
        for turn_moves in self.turns:
            print(" ".join(turn_moves))

    def _finish_transits(self, turn_log: List[str],
                         moved_this_turn: set[int]) -> None:

        for drone in self.drones:
            if drone.delivered or drone.current_connection is None:
                continue

            drone.transit_turns_left -= 1

            if drone.transit_turns_left > 0:
                continue

            drone.finish_transit()

            if drone.current_zone is None:
                continue

            turn_log.append(f"D{drone.drone_id}-{drone.current_zone.name}")
            moved_this_turn.add(drone.drone_id)

            if drone.current_zone == self.graph.end_zone:
                drone.delivered = True
