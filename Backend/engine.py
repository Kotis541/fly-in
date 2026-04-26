from Backend.graph import Drone, Hub, Connection, Map


class Engine:
    """Core simulation engine that handles pathfinding
        and drone movements across the map.
    """
    def __init__(self, map_obj: Map, drones: list[Drone]) -> None:
        """Initializes the simulation engine with map and a list of drones."""
        self.map_obj = map_obj
        self.drones = drones
        self.turn = 0
        self.log: list[str] = []
        self.visual_log: list[str] = []

        if self.map_obj.start_hub:
            self.map_obj.start_hub.capacity = float("inf")
        if self.map_obj.end_hub:
            self.map_obj.end_hub.capacity = float("inf")

    def find_path(self, start: Hub, end: Hub) -> list[Hub]:
        """Finds and returns the shortest path between the start and end."""
        distances = {}
        visited: set[Hub] = set()
        parents = {}

        for hub in self.map_obj.hubs.values():
            distances[hub] = float("inf")
        distances[start] = 0

        while len(visited) < len(self.map_obj.hubs):
            current = None
            min_dist = float("inf")

            for hub in self.map_obj.hubs.values():
                if hub not in visited and distances[hub] < min_dist:
                    current = hub
                    min_dist = distances[hub]
            if current is None or current == end:
                break

            for connection in current.connections:
                neighbor = (connection.node_b if connection.node_a == current
                            else connection.node_a)

                if neighbor not in visited:
                    if neighbor.z_type == "blocked":
                        continue

                    cost = self.get_zone_cost(neighbor)
                    new_dist = distances[current] + cost

                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        parents[neighbor] = current

            visited.add(current)

        path = []
        current = end
        while current is not None:
            path.append(current)
            current = parents.get(current)

        path.reverse()
        return path

    def get_zone_cost(self, hub: Hub) -> float:
        """Returns the cost for a given hub based on its zone type."""
        if hub.z_type == "restricted":
            return 2
        elif hub.z_type == "blocked":
            return float("inf")
        else:
            return 1

    def find_conn(self, hub_a: Hub, hub_b: Hub) -> Connection:
        """Finds and returns the connection between two adjacent hubs."""
        for conn in hub_a.connections:
            if (conn.node_a == hub_a and conn.node_b == hub_b) or \
               (conn.node_a == hub_b and conn.node_b == hub_a):
                return conn
        raise ValueError(f"Empty connection between {hub_a.name}"
                         f"and {hub_b.name}")

    def run_simulation(self) -> list[str]:
        """Executes the simulation and returns the movement log."""
        start = self.map_obj.start_hub
        end = self.map_obj.end_hub
        if start is None or end is None:
            return []
        for drone in self.drones:
            drone.path = self.find_path(start, end)

        while not all(drone.delivered for drone in self.drones):
            approved = []
            moves_this_turn = []

            for drone in self.drones:
                if drone.delivered:
                    continue

                if drone.path_index + 1 < len(drone.path):
                    next_hub = drone.path[drone.path_index + 1]
                    approved.append((drone, next_hub))

                else:
                    drone.delivered = True

            if not approved:
                break

            for drone, next_hub in approved:
                current_hub = drone.path[drone.path_index]
                connection = self.find_conn(current_hub, next_hub)

                if drone.in_transit:
                    drone.turns_in_transit -= 1
                    if drone.turns_in_transit <= 0:
                        # Musí TEĎKA dorazit!
                        if len(next_hub.drones) < next_hub.capacity:
                            next_hub.accept_drone(drone.drone_id)
                            drone.path_index += 1
                            drone.location = drone.path[drone.path_index]
                            drone.in_transit = False
                            connection.release_drone(drone.drone_id)
                        else:
                            drone.turns_in_transit = 0
                else:
                    if (len(next_hub.drones) < next_hub.capacity and
                       len(connection.connection) <
                       connection.max_link_capacity):

                        if next_hub.z_type == "restricted":
                            current_hub.release_drone(drone.drone_id)
                            connection.accept_drone(drone.drone_id)
                            drone.in_transit = True
                            drone.turns_in_transit = 2
                            drone.transit_target = next_hub
                            moves_this_turn.append(f"{drone.name}-"
                                                   f"{next_hub.name}")
                        else:
                            # Normální pohyb
                            current_hub.release_drone(drone.drone_id)
                            next_hub.accept_drone(drone.drone_id)
                            connection.accept_drone(drone.drone_id)
                            drone.path_index += 1
                            drone.location = drone.path[drone.path_index]
                            moves_this_turn.append(f"{drone.name}"
                                                   f"-{next_hub.name}")
                            connection.release_drone(drone.drone_id)
            if moves_this_turn:
                self.log.append(" ".join(moves_this_turn))
            self.visual_log.append(" ".join(moves_this_turn))

            self.turn += 1
        return self.log

    def coord_scale(self, hub_x: int, hub_y: int, screen_w: int,
                    screen_h: int, padding: int = 80) -> tuple[int, int]:
        """Scales map coordinates to fit within the
        specified screen dimensions.
        """
        min_x = min(hub.x for hub in self.map_obj.hubs.values())
        max_x = max(hub.x for hub in self.map_obj.hubs.values())
        min_y = min(hub.y for hub in self.map_obj.hubs.values())
        max_y = max(hub.y for hub in self.map_obj.hubs.values())

        data_width = max_x - min_x
        data_height = max_y - min_y

        if data_width == 0:
            data_width = 1
        if data_height == 0:
            data_height = 1

        drawable_width = screen_w - (2 * padding)
        drawable_height = screen_h - (2 * padding)

        scale_x = drawable_width / data_width
        scale_y = drawable_height / data_height

        final_x = padding + ((hub_x - min_x) * scale_x)
        final_y = padding + ((hub_y - min_y) * scale_y)

        return int(final_x), int(final_y)
