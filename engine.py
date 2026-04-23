from classes import *

class Engine:
    def __init__(self, map_obj: Map, drones: list[Drone]):
        self.map_obj = map_obj
        self.drones = drones
        self.turn = 0
        self.log = []

        if self.map_obj.start_hub:
            self.map_obj.start_hub.capacity = float("inf")
        if self.map_obj.end_hub:
            self.map_obj.end_hub.capacity = float("inf")
    
    def find_path(self, start: Hub, end: Hub) -> list[Hub]:
        distances = {}
        visited = set()
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
                neighbor = connection.node_b if connection.node_a == current else connection.node_a

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

    def get_zone_cost(self, hub: Hub) -> int:
        if hub.z_type == "restricted":
            return 2
        elif hub.z_type == "blocked":
            return float("inf")
        else:
            return 1
    
    def find_conn(self, hub_a: Hub, hub_b: Hub) -> Connection:
        for conn in hub_a.connections:
            if (conn.node_a == hub_a and conn.node_b == hub_b) or \
               (conn.node_a == hub_b and conn.node_b == hub_a):
                return conn
        raise ValueError(f"Empty connection between {hub_a.name} and {hub_b.name}")

    def run_simulation(self) -> list[str]:
        for drone in self.drones:
            drone.path = self.find_path(self.map_obj.start_hub, self.map_obj.end_hub)

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
            
            for drone, next_hub in approved:
                current_hub = drone.path[drone.path_index]
                connection = self.find_conn(current_hub, next_hub)

                if drone.in_transit:
                    drone.turns_in_transit -= 1
                    if drone.turns_in_transit <= 0:
                        # Musí TEĎKA dorazit!
                        if len(next_hub.drones) < next_hub.capacity:  # Musí se vejít!
                            next_hub.accept_drone(drone.drone_id)
                            drone.path_index += 1
                            drone.location = drone.path[drone.path_index]
                            drone.in_transit = False
                            connection.release_drone(drone.drone_id)
                        else:
                            drone.turns_in_transit = 0 # Hub je plný, dron musí počkat
                else:
                    if len(next_hub.drones) < next_hub.capacity and \
                        len(connection.connection) < connection.max_link_capacity:
                        
                        if next_hub.z_type == "restricted":
                            # ZAHÁJIT TRANZIT - nepohybovat se ještě!
                            current_hub.release_drone(drone.drone_id)
                            connection.accept_drone(drone.drone_id)
                            drone.in_transit = True
                            drone.turns_in_transit = 2  # Zbývají 2 turny
                            drone.transit_target = next_hub
                            moves_this_turn.append(f"{drone.name}-{next_hub.name}")
                        else:
                            # Normální pohyb
                            current_hub.release_drone(drone.drone_id)
                            next_hub.accept_drone(drone.drone_id)
                            connection.accept_drone(drone.drone_id)
                            drone.path_index += 1
                            drone.location = drone.path[drone.path_index]
                            moves_this_turn.append(f"{drone.name}-{next_hub.name}")
                            connection.release_drone(drone.drone_id)
            if moves_this_turn:
                self.log.append(" ".join(moves_this_turn))

            self.turn += 1
        return self.log
