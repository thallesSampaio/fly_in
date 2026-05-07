from src.MapParser import MapParser
import sys


if __name__ == "__main__":
    argv: list[str] = sys.argv
    argc: int = len(sys.argv)
    if argc == 2:
        try:
            res = MapParser.load_data(sys.argv[1])
            graph = res[0]
            drones = res[1]
            graph.debug_print()
            for item in drones:
                print(item.drone_id)
        except Exception as e:
            print(e)
