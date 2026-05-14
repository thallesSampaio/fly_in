from src.MapParser import MapParser
from src.simulator import Simulator
from src.Visualizer import GraphView
import sys


if __name__ == "__main__":
    argv: list[str] = sys.argv
    argc: int = len(sys.argv)
    if argc == 2:
        try:
            res = MapParser.load_data(sys.argv[1])
            graph = res[0]
            drones = res[1]
            view = GraphView(graph)
            sim = Simulator(graph, drones)
            view.run()
            sim.run()
            sim.display_results()
        except Exception as e:
            print(e)
