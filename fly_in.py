from src.MapParser import MapParser
from src.pathfinder import Pathfinder
from src.simulator import Simulator
import sys


if __name__ == "__main__":
    argv: list[str] = sys.argv
    argc: int = len(sys.argv)
    if argc == 2:
        try:
            res = MapParser.load_data(sys.argv[1])
            graph = res[0]
            drones = res[1]
            pathfinder = Pathfinder(graph)
            graph.debug_print()
            for item in drones:
                print(item.drone_id)
            path = pathfinder.bfs()
            print(" -> ".join(zone.name for zone in path))
            sim = Simulator(graph, drones)
            sim.run()
            sim.display_results()
        except Exception as e:
            print(e)
