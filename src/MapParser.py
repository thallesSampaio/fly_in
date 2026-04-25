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

        return raw_data
