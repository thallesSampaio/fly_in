from typing import Set, Optional, List, Dict
from enum import Enum


class ZoneType(Enum):
    """It represents the types of zones.s"""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    def movement_cost(self) -> int:
        """Return the turns needed to pass through an zone."""
        if self == ZoneType.RESTRICTED:
            return 2
        return 1


class Zone:
    """Represents a node in a graph."""

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
        """Returns whether this node has the capacity to store new drones."""

        if self.is_start or self.is_end:
            return True
        return len(self.current_drones) < self.max_drones

    def add_drone(self, drone_id: int) -> None:
        """Add a drone ID to the current_drones set."""

        self.current_drones.add(drone_id)

    def remove_drone(self, drone_id: int) -> None:
        """Remove a drone ID from the current_drones set."""

        self.current_drones.discard(drone_id)


class Connection:
    """Represents an edge in a graph."""

    def __init__(self, zone_a: Zone, zone_b: Zone,
                 max_capacity: int = 1) -> None:
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_capacity = max_capacity
        self.current_drones: Set[int] = set()

    def get_other(self, zone: Zone) -> Zone:
        """Receives a node representing the current zone
        and returns the other zone on that edge."""

        if zone == self.zone_a:
            return self.zone_b
        elif zone == self.zone_b:
            return self.zone_a
        raise ValueError(f"Zone '{zone.name}' is not part of this connection.")

    def has_capacity(self) -> bool:
        return len(self.current_drones) < self.max_capacity

    def enter(self, drone_id: int) -> None:
        self.current_drones.add(drone_id)

    def leave(self, drone_id: int) -> None:
        self.current_drones.discard(drone_id)


class ParsedConnection:
    """Represents an edge as a string before becoming a Connection object."""
    def __init__(self, zone_a: str, zone_b: str,
                 max_capacity: int = 1) -> None:
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_capacity = max_capacity


class Drone:
    """Represents a drone."""

    def __init__(self, drone_id: int) -> None:
        self.drone_id = drone_id
        self.current_zone: Optional[Zone] = None
        self.path: List[Zone] = []
        self.path_index: int = 0
        self.delivered: bool = False
        self.current_connection: Optional[Connection] = None
        self.transit_dest: Optional[Zone] = None
        self.transit_turns_left: int = 0

    def start_transit(self, next_zone: Zone, connection: Connection) -> None:
        """Start moving toward a restricted zone. (2 turns)."""

        if not connection.has_capacity():
            return

        if self.current_zone is not None:
            self.current_zone.remove_drone(self.drone_id)

        connection.enter(self.drone_id)
        self.current_connection = connection
        self.transit_dest = next_zone
        self.transit_turns_left = next_zone.zone_type.movement_cost() - 1

    def finish_transit(self) -> None:
        """Arrive at the restricted zone."""

        if self.transit_dest is None:
            return

        if self.current_connection is not None:
            self.current_connection.leave(self.drone_id)

        self.current_zone = self.transit_dest
        self.current_zone.add_drone(self.drone_id)
        self.path_index += 1

        self.current_connection = None
        self.transit_dest = None
        self.transit_turns_left = 0

    def get_next_zone(self) -> Optional[Zone]:
        """Gets the next zone in the list of paths."""

        if self.path_index + 1 < len(self.path):
            return self.path[self.path_index + 1]
        return None

    def move_to_next(self) -> None:
        """Move the drone to the next zone in the list of paths."""
        next_zone = self.get_next_zone()

        if next_zone is None:
            return

        if self.current_zone is not None:
            self.current_zone.remove_drone(self.drone_id)

        self.current_zone = next_zone
        self.current_zone.add_drone(self.drone_id)
        self.path_index += 1


class Graph:
    """Represents a graph constructed from map data."""

    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.start_zone: Optional[Zone] = None
        self.end_zone: Optional[Zone] = None
        self.__connection_keys: set[tuple[str, str]] = set()

    def add_zone(self, zone: Zone) -> None:
        """Add a Node to the graph."""

        if zone.name in self.zones:
            raise ValueError(f"Duplicate zone '{zone.name}'.")

        self.zones[zone.name] = zone
        if zone.is_start:
            self.start_zone = zone
        if zone.is_end:
            self.end_zone = zone

    def add_connection(self, zone_a_name: str,
                       zone_b_name: str,
                       max_capacity: int = 1) -> None:
        """Add an edge to the graph."""

        if zone_a_name not in self.zones:
            raise ValueError(f"Unknown zone '{zone_a_name}'.")

        if zone_b_name not in self.zones:
            raise ValueError(f"Unknown zone '{zone_b_name}'.")

        a, b = sorted((zone_a_name, zone_b_name))
        key: tuple[str, str] = (a, b)

        if key in self.__connection_keys:
            raise ValueError("Duplicate connection"
                             f" '{zone_a_name}-{zone_b_name}'.")

        self.__connection_keys.add(key)

        zone_a = self.zones[zone_a_name]
        zone_b = self.zones[zone_b_name]
        conn = Connection(zone_a, zone_b, max_capacity)
        self.connections.append(conn)
        zone_a.neighbours.append(conn)
        zone_b.neighbours.append(conn)

    def get_zone(self, name: str) -> Zone:
        """Get a zone by name."""
        if name not in self.zones:
            raise ValueError(f"Zone '{name}' not found.")
        return self.zones.get(name, self.zones[name])

    def get_valid_neighbours(self, zone: Zone) -> List[Zone]:
        """Gets the accessible zones connected to the zone
        passed as a parameter."""

        result = []
        for conn in zone.neighbours:
            neighbor = conn.get_other(zone)
            if neighbor.zone_type != ZoneType.BLOCKED:
                result.append(neighbor)
        return result

    def get_connection_between(self, zone_a: Zone,
                               zone_b: Zone) -> Connection | None:
        for connection in zone_a.neighbours:
            if connection.get_other(zone_a) == zone_b:
                return connection

        return None

    def debug_print(self) -> None:
        print("=== GRAPH ===\n")

        print("Zones:")
        for zone in self.zones.values():
            flags = []
            if zone.is_start:
                flags.append("START")
            if zone.is_end:
                flags.append("END")

            flag_str = f" ({', '.join(flags)})" if flags else ""
            print(f"- {zone.name}{flag_str} "
                  f"[type={zone.zone_type.value}, cap={zone.max_drones}]")

        print("\nConnections:")
        for conn in self.connections:
            print(f"- {conn.zone_a.name} <-> {conn.zone_b.name} "
                  f"(cap={conn.max_capacity})")

        print("\n================\n")
