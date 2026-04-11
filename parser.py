from classes import Drone, Hub, Map, Connection
from typing import Tuple


def extract_hub_coords(line: str) -> tuple[str, int, int]:
    parts = line.split()
    return parts[1], int(parts[2]), int(parts[3])


def parse_metadata(line: str) -> dict[str, str]:
    if "[" not in line:
        return {}
    
    start = line.find("[") + 1
    end = line.find("]")
    metadata_str = line[start:end]

    meta_dict = {}
    for meta in metadata_str.split():
        if "=" in meta:
            key, value = meta.split("=")
            meta_dict[key] = value
    return meta_dict


def parse_file(filepath: str) -> Tuple[Map, list[Drone]]:
    map = Map()
    with open(filepath, 'r') as file:
        for line in file:
            if line.startswith("#"):
                continue

            if line.startswith("nb_drones:"):
                nb_drones = int(line.split(":")[1])

            elif line.startswith(("start_hub:", "end_hub:", "hub:")):
                name, x, y = extract_hub_coords(line)
                meta_dict = parse_metadata(line)

                capacity = int(meta_dict.get("max_drones", 1))
                z_type = meta_dict.get("zone", "normal")

                hub = Hub(name=name, z_type=z_type, x=x, y=y, capacity=capacity)
                map.add_hub(hub)

                if line.startswith("start_hub:"):
                    map.start_hub = hub
                elif line.startswith("end_hub:"):
                    map.end_hub = hub
            
            elif line.startswith("connection:"):
                meta_dict = parse_metadata(line)
                parts = line.split()

                a, b = parts[1].split("-")
                capacity = int(meta_dict.get("max_link_capacity", 1))
                node_a = map.hubs[a]
                node_b = map.hubs[b]

                new_connetion = Connection(node_a, node_b, capacity)
                node_a.add_connection(new_connetion)
                node_b.add_connection(new_connetion)

    drones_list = []
    for i in range(1, nb_drones + 1):
        name = f"D{i}"

        drone = Drone(name, i, map.start_hub)
        drones_list.append(drone)
        map.start_hub.accept_drone(drone)
    return map, drones_list
