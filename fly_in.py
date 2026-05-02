from src.MapParser import MapParser
from src.models import Zone
import sys


if __name__ == "__main__":
    argv: list[str] = sys.argv
    argc: int = len(sys.argv)
    if argc == 2:
        try:
            res = MapParser.load_data(sys.argv[1])
            zones = res[0]
            conn = res[1]
            for item in zones:
                print(item.name, item.x, item.y)
            for item in conn:
                print(item.zone_a, item.zone_b)
        except Exception as e:
            print(e)
