from src import Connection
from typing import List


class Zone:
    def __init__(self, name: str, x: int, y: int, zone_type: str = "normal",
                 max_drones: int = 1, color: str | None = None):
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.max_drones = max_drones
        self.color = color
        self.neighbours: List[Connection] = []
