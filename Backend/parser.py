from Backend.graph import Drone, Hub, Map, Connection
from typing import Tuple


class Parser:
    @staticmethod
    def extract_hub_coords(line: str) -> tuple[str, int, int]:
        """Parses and returns the hub name and coordinates from a line."""
        parts = line.split()
        if len(parts) < 4:
            raise ValueError("[ERROR - PARSER]: "
                             f"Invalid hub coordinates ({line})")
        name = parts[1]
        try:
            x = int(parts[2])
            y = int(parts[3])
        except ValueError:
            raise ValueError("[ERROR - PARSER]: Invalid "
                             f"type of coord ({line})")
        return name, x, y

    @staticmethod
    def parse_metadata(line: str, p_type: str) -> dict[str, str]:
        """Extracts and parses metadata key-value pairs enclosed in
        brackets.
        """
        if "[" not in line:
            return {}

        start = line.find("[") + 1
        end = line.find("]")
        metadata_str = line[start:end]

        meta_dict = {}
        valid_key_hub = ["zone", "color", "max_drones"]
        valid_key_conn = ["max_link_capacity"]
        for meta in metadata_str.split():
            if "=" in meta:
                key, value = meta.split("=", 1)
                if p_type == "hub" and key not in valid_key_hub:
                    raise ValueError("[ERROR - PARSER]: "
                                     "Invalid metadata type (parsing hub)")
                if p_type == "connection" and key not in valid_key_conn:
                    raise ValueError("[ERROR - PARSER]: Invalid "
                                     "metadata type (parsing connection)")
                meta_dict[key] = value
            else:
                raise ValueError("[ERROR - PARSER]: "
                                 "Invalid metadata format, expected key=value")

        return meta_dict

    @staticmethod
    def parse_file(filepath: str) -> Tuple[Map, list[Drone]]:
        """Parses the input file to construct and return the Map and
        list of Drones.
        """
        map = Map()
        nb_drones = 0
        nb_drones_found = False
        seen_connection: set[frozenset[str]] = set()
        with open(filepath, 'r') as file:
            for line_num, raw_line in enumerate(file, 1):
                line = raw_line.strip()
                if line.startswith("#") or line == "":
                    continue
                if not nb_drones_found:
                    if not line.startswith("nb_drones:"):
                        raise ValueError(
                            f"[ERROR - PARSER] Line {line_num}: "
                            f"First non-comment line must be 'nb_drones:'"
                        )
                    try:
                        nb_drones = int(line.split(":")[1].strip())
                    except ValueError:
                        raise ValueError(
                            f"[ERROR - PARSER] Line {line_num}: "
                            f"nb_drones must be a positive integer"
                        )
                    if nb_drones <= 0:
                        raise ValueError(
                            f"[ERROR - PARSER] Line {line_num}: "
                            f"nb_drones must be positive"
                        )
                    nb_drones_found = True
                    continue                

                elif line.startswith(("start_hub:", "end_hub:", "hub:")):
                    valid_zone = ["normal", "blocked",
                                "restricted", "priority"]
                    try:
                        name, x, y = Parser.extract_hub_coords(line)
                        meta_dict = Parser.parse_metadata(line, "hub")

                        capacity = int(meta_dict.get("max_drones", 1))
                        z_type = meta_dict.get("zone", "normal")
                        color = meta_dict.get("color", None)
                    except ValueError as e:
                        raise ValueError(e)
                    if z_type not in valid_zone:
                        raise ValueError("[ERROR - PARSER]: Invalid zone!")

                    hub = Hub(name=name, z_type=z_type, x=x, y=y,
                            capacity=capacity, color=color)
                    map.add_hub(hub)

                    if line.startswith("start_hub:"):
                        if map.start_hub is not None:
                            raise ValueError("[ERROR - PARSER]: "
                                             "Map cant have more than 1 start!")
                        map.start_hub = hub
                    elif line.startswith("end_hub:"):
                        if map.end_hub is not None:
                            raise ValueError("[ERROR - PARSER]: "
                                             "Map cant have more than 1 end!")
                        map.end_hub = hub

                elif line.startswith("connection:"):
                    try:
                        meta_dict = Parser.parse_metadata(line, "connection")
                        parts = line.split()
                    except ValueError as e:
                        raise ValueError(e)

                    a, b = parts[1].split("-")
                    capacity = int(meta_dict.get("max_link_capacity", 1))
                    if a not in map.hubs or b not in map.hubs:
                        raise ValueError("[ERROR - PARSER]:"
                                         "Connection references unknown hub: "
                                         f"{a} or {b}")
                    if a == b:
                        raise ValueError("[ERROR - PARSER]: "
                                         "Node {a} can't connect to itself")
                    conn_key = frozenset([a, b])
                    if conn_key in seen_connection:
                        raise ValueError(f"[ERROR - PARSER]: Duplicate connection between {a} and {b}")
                    seen_connection.add(conn_key)
                    node_a = map.hubs[a]
                    node_b = map.hubs[b]

                    new_connetion = Connection(node_a, node_b, capacity)
                    node_a.add_connection(new_connetion)
                    node_b.add_connection(new_connetion)

            if map.start_hub is None:
                raise ValueError("[ERROR - PARSER]: You didn't add start_hub!")
            if map.end_hub is None:
                raise ValueError("[ERROR - PARSER]: You didn't add end_hub!")

            if nb_drones <= 0:
                raise ValueError("[ERROR - PARSER]: "
                                 f"Invalid number of drones ({nb_drones})")

            map.start_hub.capacity = float('inf')
            map.end_hub.capacity = float('inf')

            drones_list = []
            for i in range(1, nb_drones + 1):
                name = f"D{i}"
                drone = Drone(name, i, map.start_hub)
                drones_list.append(drone)
                map.start_hub.accept_drone(drone.drone_id)

            return map, drones_list
