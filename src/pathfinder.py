from collections import deque
from src.models import Graph, Zone
from typing import List


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

            for neighbor in self.graph.get_accessible_neighbours(current_zone):
                if neighbor.name not in visited:
                    visited.add(neighbor.name)
                    queue.append((neighbor, path + [neighbor]))
        return []
