from collections import deque
from src.models import Graph, Zone
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

    def dijkstra(self) -> List[Zone]:
        """trying to implement dijkstra"""
        if self.graph.start_zone is None:
            raise ValueError("Pathfinder - Error: missing start zone.")
        if self.graph.end_zone is None:
            raise ValueError("Pathfinder - Error: missing end zone.")

        start = self.graph.start_zone
        end = self.graph.end_zone

        heap: List[Tuple[int, str]] = [(0, start.name)]
        prev: Dict[str, Optional[Zone]] = {start.name: None}
        dist: Dict[str, int] = {start.name: 0}

        while heap:
            cost, current_name = heapq.heappop(heap)
            current_zone = self.graph.zones[current_name]

            if current_zone == end:
                break

            if cost > dist.get(current_name, float('inf')):
                continue

            for neighbour in self.graph.get_valid_neighbours(current_zone):
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
