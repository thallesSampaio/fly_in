import sys
from src.map_parser import MapParser
from src.simulator import Simulator

try:
    from src.visualizer import GraphView
except ModuleNotFoundError:
    print("ModuleNotFoundError - Missing module: 'customtkinter'."
          "\nPlease run 'make install' and 'source venv/bin/activate'.")
    sys.exit(1)


def run_application() -> None:
    """Run and manage the application flow and handle user input errors."""
    argv: list[str] = sys.argv
    argc: int = len(sys.argv)

    if argc != 2:
        print("Missing map. Run 'python3 fly_in.py example_map.txt'.")
        sys.exit(1)

    try:
        map_file = argv[1]

        res = MapParser.load_data(map_file)
        graph = res[0]
        drones = res[1]

        view = GraphView(graph, drones)
        sim = Simulator(graph, drones)

        sim.setup()
        view.set_on_next_turn(sim.step)
        view.draw()
        view.run()
        sim.display_results()

        print(len(sim.turns))
        sys.exit(0)

    except FileNotFoundError as e:
        print(f"Map file not found. {e.strerror}: '{e.filename}'.")
        sys.exit(1)
    except PermissionError as e:
        print(f"No permission to map file. {e.strerror}: '{e.filename}'.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
