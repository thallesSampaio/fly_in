from src.models import (Zone, ZoneType, Drone, Graph, ParsedConnection)
from typing import List


class MapParser:
    """Class responsible for parsing and validating map files."""

    valid_keys: list[str] = [
        "nb_drones", "start_hub", "end_hub",
        "hub", "connection"
    ]
    zones_keys: list[str] = ["start_hub", "end_hub", "hub"]

    @classmethod
    def load_data(cls, filename: str) -> tuple[Graph, List[Drone]]:
        """Load data from the map files"""

        graph = Graph()
        list_drones: list[Drone] = []
        dup_helper: set[str] = set()
        first_valid_line = True

        with open(filename, "r") as file:
            for i, line in enumerate(file, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                key, value = cls.__parse_key_value(i, line)

                if first_valid_line:
                    if key != "nb_drones":
                        raise ValueError(f"Line {i}: First line must define"
                                         " nb_drones.")
                    first_valid_line = False

                if key != "hub" and key != "connection":
                    if key in dup_helper:
                        raise ValueError(f"Duplicate key found at line {i}: "
                                         f"'{key}'.")
                if not value:
                    raise ValueError(f"Empty value for key '{key}' "
                                     f"at line {i}.")

                if key in cls.zones_keys:
                    zone = cls.__parse_hub(i, value)
                    if key == "start_hub":
                        zone.is_start = True
                    elif key == "end_hub":
                        zone.is_end = True
                    graph.add_zone(zone)
                    dup_helper.add(key)
                elif key == "connection":
                    conn: ParsedConnection = cls.__parse_connection(i, value)
                    graph.add_connection(conn.zone_a,
                                         conn.zone_b, conn.max_capacity)
                elif key == "nb_drones":
                    list_drones = cls.__parse_nb_drones(i, value)
                    dup_helper.add(key)

        required = {"nb_drones", "start_hub", "end_hub"}
        missing = required - dup_helper

        if missing:
            raise ValueError(f"Missing required keys: {', '.join(missing)}.")

        return (graph, list_drones)

    @classmethod
    def __parse_nb_drones(cls, line_number: int, value: str) -> list[Drone]:
        """Parse and validate nb_drones line."""

        try:
            nb_drones = int(value)
        except ValueError:
            raise ValueError(f"Line {line_number}:"
                             " nb_drones must be an integer.")

        if nb_drones < 1:
            raise ValueError(f"Line {line_number}: nb_drones must be positive"
                             " and higher than 0.")

        return [Drone(i) for i in range(1, nb_drones + 1)]

    @classmethod
    def __parse_hub(cls, line_number: int, value: str) -> Zone:
        """Parse and validate hub line."""

        valid_metadata = {"zone", "color", "max_drones"}
        parts = value.split()
        if len(parts) < 3:
            raise ValueError(f"Line {line_number}:"
                             " Hub format must be 'name x y [metadata]'")

        name = parts[0]
        if "-" in name:
            raise ValueError(f"Line {line_number}:"
                             " Zone names cannot contain dashes ('-')")

        try:
            x = int(parts[1])
            y = int(parts[2])
        except ValueError:
            raise ValueError(f"Line {line_number}:"
                             " Zone coordinates must be integers, got"
                             f" '{parts[1]}' and '{parts[2]}'.")

        metadata_str = " ".join(parts[3:]) if len(parts) > 3 else ""
        metadata = cls.__parse_metadata(line_number, metadata_str)
        for key in metadata:
            if key not in valid_metadata:
                raise ValueError(f"Line {line_number}: Invalid hub metadata"
                                 f" '{key}'.")
        type_str = metadata.get("zone", "normal").lower()
        try:
            zone_type = ZoneType(type_str)
        except ValueError:
            raise ValueError(f"Line {line_number}: "
                             f"Invalid zone type '{type_str}'. ")
        color = metadata.get("color")
        try:
            max_drones = int(metadata.get("max_drones", "1"))
        except ValueError:
            raise ValueError(f"Line {line_number}:"
                             " max_drones must be an integer.")
        if max_drones < 1:
            raise ValueError(f"Line {line_number}: max_drones"
                             " must be higher than 0.")

        return Zone(name=name, x=x, y=y, zone_type=zone_type, color=color,
                    max_drones=max_drones)

    @classmethod
    def __parse_connection(cls, line_number: int,
                           value: str) -> ParsedConnection:
        """Parse and validate conneciton line."""

        parts = value.split()
        if len(parts) < 1:
            raise ValueError(f"Line {line_number}: Empty connection.")

        connection_name = parts[0]

        if "-" not in connection_name:
            raise ValueError(f"Line {line_number}: "
                             "Connection must be in format 'zoneA-zoneB'.")

        zone_names = connection_name.split("-")

        if len(zone_names) != 2:
            raise ValueError(f"Line {line_number}: "
                             "Connection must contain exactly two zones.")

        zone_a = zone_names[0]
        zone_b = zone_names[1]

        if not zone_a or not zone_b:
            raise ValueError(f"Line {line_number}: "
                             "Connection zones cannot be empty.")

        metadata_str = " ".join(parts[1:]) if len(parts) > 1 else ""
        metadata = cls.__parse_metadata(line_number, metadata_str)

        for key in metadata:
            if key != "max_link_capacity":
                raise ValueError(f"Line {line_number}: "
                                 f"Invalid connection metadata '{key}'.")

        try:
            capacity = metadata.get("max_link_capacity", "1")
            max_capacity = int(capacity)
        except ValueError:
            raise ValueError(f"Line {line_number}: "
                             "Invalid capacity value "
                             f"'{capacity}' must be an integer.")

        if max_capacity < 1:
            raise ValueError(f"Line {line_number}: max_capacity"
                             " must be higher than 0.")

        return ParsedConnection(zone_a=zone_a, zone_b=zone_b,
                                max_capacity=max_capacity)

    @classmethod
    def __parse_metadata(cls, line_number: int,
                         metadata: str) -> dict[str, str]:
        """Parse and validate metadata."""

        if not metadata:
            return {}

        if not metadata.startswith("[") or not metadata.endswith("]"):
            raise ValueError(f"Line {line_number}: Invalid metadata format.")

        content = metadata[1:-1].strip()
        parsed: dict[str, str] = {}

        if not content:
            return parsed

        for item in content.split():
            if "=" not in item:
                raise ValueError(
                    f"Line {line_number}: Invalid metadata item '{item}'.")

            key, value = item.split("=", 1)

            if not key or not value:
                raise ValueError(
                    f"Line {line_number}: Invalid metadata item '{item}'.")

            if key in parsed:
                raise ValueError(
                    f"Line {line_number}: Duplicate metadata key '{key}'.")

            parsed[key] = value

        return parsed

    @classmethod
    def __parse_key_value(cls, line_number: int, line: str) -> tuple[str, str]:
        """Read line, split key-value and validate."""

        if ":" not in line:
            raise ValueError(f"Line {line_number}: Missing ':'.")

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if key not in cls.valid_keys:
            raise ValueError(f"Line {line_number}: Invalid key '{key}'.")

        if not value:
            raise ValueError(f"Line {line_number}: Empty value for '{key}'.")

        return key, value
