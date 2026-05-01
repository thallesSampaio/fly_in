from src.Zone import Zone


class MapParser:

    valid_keys: list[str] = [
        "nb_drones", "start_hub", "end_hub",
        "hub", "connection"
    ]
    loaded_keys: list[str] = [
        "nb_drones", "start_hub", "end_hub",
        "hubs", "connections"
    ]

    @classmethod
    def load_data(cls, filename: str) -> dict[str, dict | str]:
        """Load data from the map files"""

        list_hubs: list[Zone] = []
        raw_data: dict[str, dict | str] = {}
        hubs: dict[str, str] = {}
        connections: dict[str, str] = {}

        with open(filename, "r") as file:
            for i, line in enumerate(file, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if ":" not in line:
                    raise ValueError(f"Invalid format at line {i}:"
                                     " missing ':'.")

                parts = line.split(":", 1)
                key = parts[0].strip()
                value = parts[1].strip()

                if key not in cls.valid_keys:
                    raise ValueError(f"Invalid key at line {i}: '{key}'.")
                if key != "hub" and key != "connection":
                    if key in raw_data:
                        raise ValueError(f"Duplicate key found at line {i}: "
                                         f"'{key}'.")
                if not value:
                    raise ValueError(f"Empty value for key '{key}' "
                                     f"at line {i}.")

                if key == "hub":
                    item: Zone = cls.__parse_hub(i, value)
                    list_hubs.append(item)
                    split = value.split(" ", 1)
                    name = split[0]
                    value = split[1]
                    hubs[name] = value
                elif key == "connection":
                    split = value.split(" ", 1)
                    name = split[0]
                    if len(split) > 1:
                        value = split[1].split("=", 1)[1]
                        value = value.removesuffix("]")
                        connections[name] = value
                    else:
                        connections[name] = "1"
                else:
                    raw_data[key] = value

            raw_data["hubs"] = hubs
            raw_data["connections"] = connections

            for key in cls.loaded_keys:
                if key not in raw_data.keys():
                    raise ValueError(f"Missing key: '{key}'.")
        for item in list_hubs:
            print(item.name, item.x, item.y)
        return raw_data

    @classmethod
    def __parse_hub(cls, line_number: int, value: str) -> Zone:
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
                             " Coordinates must be integers")

        # metadata_str = " ".join(parts[3:]) if len(parts) > 3 else ""

        return Zone(name=name, x=x, y=y)
