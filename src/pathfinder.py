from collections import deque
from src.models import Graph, Zone, Drone
from typing import List, Tuple, Dict, Optional
import heapq


class Pathfinder:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def bfs(self) -> List[Zone]:
        if self.graph.start_zone is None:
            raise ValueError("Pathfinder - Error: missing start zone.")
        if self.graph.end_zone is None:
            raise ValueError("Pathfinder - Error: missing end zone.")
        start = self.graph.start_zone
        end = self.graph.end_zone

        queue = deque([(start, [start])])
        visited = {start.name}

        while queue:
            current_zone, path = queue.popleft()

            if current_zone == end:
                return path

            for neighbor in self.graph.get_valid_neighbours(current_zone):
                if neighbor.name not in visited:
                    visited.add(neighbor.name)
                    queue.append((neighbor, path + [neighbor]))
        return []

    def dijkstra(self, blocked: Optional[set[str]] = None) -> List[Zone]:
        """trying to implement dijkstra"""
        if self.graph.start_zone is None:
            raise ValueError("Pathfinder - Error: missing start zone.")
        if self.graph.end_zone is None:
            raise ValueError("Pathfinder - Error: missing end zone.")

        start = self.graph.start_zone
        end = self.graph.end_zone

        heap: List[Tuple[float, str]] = [(0, start.name)]
        prev: Dict[str, Optional[Zone]] = {start.name: None}
        dist: Dict[str, float] = {start.name: 0}

        while heap:
            cost, current_name = heapq.heappop(heap)
            current_zone = self.graph.zones[current_name]

            if current_zone == end:
                break

            if cost > dist.get(current_name, float('inf')):
                continue

            for neighbour in self.graph.get_valid_neighbours(current_zone):
                if neighbour.name in blocked:
                    continue
                new_cost = cost + neighbour.zone_type.movement_cost()
                if new_cost < dist.get(neighbour.name, float('inf')):
                    dist[neighbour.name] = new_cost
                    prev[neighbour.name] = current_zone
                    heapq.heappush(heap, (new_cost, neighbour.name))

        if end.name not in prev:
            return []

        path: List[Zone] = []
        node: Optional[Zone] = end
        while node is not None:
            path.append(node)
            node = prev[node.name]
        path.reverse()
        return path

    def _find_multiple_paths(self, drones: List[Drone],
                             max_paths: int) -> list[list[Zone]]:
        """Tenta encontrar multiplos caminhos apos bloquear a
        primeira zona possivel no primeiro path encontrado"""
        paths: list[list[Zone]] = []
        blocked: set[str] = set()

        for _ in range(max_paths):
            path = self.dijkstra(blocked)
            if path is None or len(path) < 2:
                break

            paths.append(path)
            if len(path) > 2:
                blocked.add(path[1].name)

        if not paths:
            raise ValueError("No path found.")

        return paths
