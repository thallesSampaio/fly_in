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
            view = GraphView(graph, drones)
            sim = Simulator(graph, drones)
            sim.setup()
            view.set_on_next_turn(sim.step)
            view.draw()
            view.run()
            sim.display_results()
        except Exception as e:
            print(e)
