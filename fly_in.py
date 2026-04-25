from src.MapParser import MapParser
import sys


if __name__ == "__main__":
    argv: list[str] = sys.argv
    argc: int = len(sys.argv)
    if argc == 2:
        try:
            res = MapParser.load_data(sys.argv[1])
            print(res)
        except Exception as e:
            print(e)
