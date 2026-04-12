from __future__ import annotations

class Connection:
    def __init__(self, node_a: Hub, node_b: Hub, max_link_capacity: int) -> None:
        self.max_link_capacity = max_link_capacity
        self.node_a = node_a
        self.node_b = node_b
        self.connection = []
    
    def accept_drone(self, id: int) -> bool:
        if len(self.connection) < self.max_link_capacity:
            self.connection.append(id)
            return True
        return False
    
    def realease_drone(self, id: int) -> None:
        self.connection.remove(id)

class Hub:
    def __init__(self, name: str, z_type: str, capacity: 1, x: int, y: int) -> None:
        self.name = name
        self.z_type = z_type
        self.capacity = capacity
        self.x = x
        self.y = y
        self.connections: list[Connection] = []
        self.drones = []

    def accept_drone(self, id: int) -> bool:
        if len(self.drones) < self.capacity:
            self.drones.append(id)
            return True
        return False

    def release_drone(self, id: int) -> None:
        self.drones.remove(id)
    
    def add_connection(self, connection: Connection):
        self.connections.append(connection)

        
class Drone:
    def __init__(self, name: str, drone_id: int, location: Hub | Connection) -> None:
        self.name = name
        self.drone_id = drone_id
        self.location = location


class Map:
    def __init__(self) -> None:
        self.hubs: dict[str, Hub] = {}
        self.start_hub: Hub | None = None
        self.end_hub: Hub | None = None
    
    def add_hub(self, hub: Hub):
        self.hubs[hub.name] = hub


class Engine:
    pass
