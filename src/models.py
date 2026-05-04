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
    
    def has_capacity(self) -> bool:
        if self.is_start or self.is_end:
            return True
        return len(self.current_drones) < self.max_drones

    def add_drone(self, drone_id: int) -> None:
        self.current_drones.add(drone_id)

    def remove_drone(self, drone_id: int) -> None:
        self.current_drones.discard(drone_id)


class Connection:
    def __init__(self,
                 zone_a: Zone, zone_b: Zone,
                 max_capacity: int = 1) -> None:
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_capacity = max_capacity
        self.current_traversing: int = 0


class Drone:
    def __init__(self, drone_id: int) -> None:
        self.drone_id = drone_id
        self.current_zone: Optional[Zone] = None
        # self.path: List[Zone] = []
        # self.path_index: int = 0
        # self.delivered: bool = False
        # self.in_transit: bool = False
        # self.transit_dest: Optional[Zone] = None
        # self.transit_turns_left: int = 0


class Graph:
    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.start_zone: Optional[Zone] = None
        self.end_zone: Optional[Zone] = None

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone
        if zone.is_start:
            self.start_zone = zone
        if zone.is_end:
            self.end_zone = zone

    def add_connection(self, zone_a_name: str,
                       zone_b_name: str,
                       max_capacity: int = 1) -> None:
        zone_a = self.zones[zone_a_name]
        zone_b = self.zones[zone_b_name]
        conn = Connection(zone_a, zone_b, max_capacity)
        self.connections.append(conn)
        zone_a.neighbours.append(conn)
        zone_b.neighbours.append(conn)

    def get_zone(self, name: str) -> Optional[Zone]:
        return self.zones.get(name)
