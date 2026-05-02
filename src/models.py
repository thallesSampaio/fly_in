from typing import Set, Optional, List
from enum import Enum


class ZoneType(Enum):
    """zone type enum"""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    def movement_cost(self) -> int:
        if self == ZoneType.RESTRICTED:
            return 2
        return 1


class Zone:
    def __init__(self,
                 name: str, x: int, y: int,
                 zone_type: ZoneType = ZoneType.NORMAL,
                 max_drones: int = 1, color: Optional[str] = None,
                 is_start: bool = False,
                 is_end: bool = False) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.max_drones = max_drones
        self.color = color
        self.neighbours: List[Connection] = []
        self.is_start = is_start
        self.is_end = is_end
        self.current_drones: Set[int] = set()


class Connection:
    def __init__(self,
                 zone_a: Zone, zone_b: Zone,
                 max_capacity: int = 1) -> None:
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_capacity = max_capacity
        self.current_traversing: int = 0
