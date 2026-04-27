from __future__ import annotations


class Connection:
    """Represents a link between two hubs with a specific maximum drone
    capacity.
    """
    def __init__(self, node_a: Hub, node_b: Hub,
                 max_link_capacity: int) -> None:
        """Initializes a connection between two hubs"""
        self.max_link_capacity = max_link_capacity
        self.node_a = node_a
        self.node_b = node_b
        self.name = f"{node_a.name}-{node_b.name}"
        self.connection: list[int] = []

    def accept_drone(self, id: int) -> bool:
        """Adds a drone to the connection if capacity allows"""
        if len(self.connection) < self.max_link_capacity:
            self.connection.append(id)
            return True
        return False

    def release_drone(self, id: int) -> None:
        """Removes a drone from the connection if it is currently in transit
        here.
        """
        if id in self.connection:
            self.connection.remove(id)


class Hub:
    """Represents a node or location on the map that can hold drones
    and connect to other hubs.
    """
    def __init__(self, name: str, z_type: str,
                 capacity: float, x: int, y: int,
                 color: str | None = None) -> None:
        """Initializes a hub with its properties, capacity, and coordinates."""
        self.name = name
        self.z_type = z_type
        self.capacity = capacity
        self.x = x
        self.y = y
        self.color = color
        self.connections: list[Connection] = []
        self.drones: list[int] = []

    def accept_drone(self, id: int) -> bool:
        """Adds a drone to the hub if there is available capacity"""
        if len(self.drones) < self.capacity:
            self.drones.append(id)
            return True
        return False

    def release_drone(self, id: int) -> None:
        """Removes a drone from the hub."""
        if id in self.drones:
            self.drones.remove(id)

    def add_connection(self, connection: Connection) -> None:
        """Links a new connection to this hub."""
        self.connections.append(connection)


class Drone:
    """Represents a delivery drone, tracking its current location, path,
    and transit state.
    """
    def __init__(self, name: str, drone_id: int,
                 location: Hub | Connection) -> None:
        """Initializes a drone with an ID and starting location."""
        self.name = name
        self.drone_id = drone_id
        self.location = location
        self.path: list[Hub] = []
        self.path_index = 0
        self.delivered = False
        self.in_transit = False
        self.transit_target: Hub | None = None
        self.turns_in_transit = 0


class Map:
    """Container class for the simulation environment, storing all hubs
    and start/end points.
    """
    def __init__(self) -> None:
        """Initializes an empty map to hold hubs and track start/end points."""
        self.hubs: dict[str, Hub] = {}
        self.start_hub: Hub | None = None
        self.end_hub: Hub | None = None

    def add_hub(self, hub: Hub) -> None:
        """Adds a hub to the map's collection."""
        self.hubs[hub.name] = hub
