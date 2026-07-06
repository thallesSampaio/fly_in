from src.models import Graph, Zone
from typing import Optional
import heapq


class Pathfinder:
    def __init__(self, graph: Graph) -> None:
        """Find valid paths between the start and end zones of a graph."""
        self.graph = graph

    def dijkstra(self, blocked: set[str]) -> list[Zone]:
        """Find the lowest-cost path while avoiding blocked zones."""
        start = self.graph.start_zone
        end = self.graph.end_zone

        heap: list[tuple[float, str]] = [(0, start.name)]
        prev: dict[str, Optional[Zone]] = {start.name: None}
        dist: dict[str, float] = {start.name: 0}

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

        path: list[Zone] = []
        node: Optional[Zone] = end
        while node is not None:
            path.append(node)
            node = prev[node.name]
        path.reverse()
        return path

    def find_multiple_paths(self, max_paths: int) -> list[list[Zone]]:
        """Try to find multiple alternative paths from start to end."""
        best = self.dijkstra(set())
        if not best:
            raise ValueError("No path found between the start and end zones.")

        found: list[list[Zone]] = [best]
        seen: set[tuple[str, ...]] = {tuple(z.name for z in best)}

        for zone in best[1:-1]:
            path = self.dijkstra({zone.name})
            if not path:
                continue
            key = tuple(z.name for z in path)
            if key not in seen:
                seen.add(key)
                found.append(path)
            if len(found) >= max_paths:
                break
        return found
