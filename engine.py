from classes import *

class Engine:
    def __init__(self, map: Map, drones: list[Drone]):
        self.map = map
        self.drones = drones
        self.turn = 0
        self.log = []
    
    def find_path(self, start: Hub, end: Hub) -> list[Hub]:
        queue = [[start]]
        visited = {start}

        while len(queue) > 0:
            current_path = queue.pop(0)
            current_hub = current_path[-1]

            if current_hub == end:
                return current_path
            for n in current_hub.connections:
                    if n.node_a == current_hub:
                        neighbor = n.node_b
                    else:
                        neighbor = n.node_a
                    if neighbor in visited:
                        continue
                    if neighbor.z_type == "blocked":
                        continue
                    visited.add(neighbor)
                    queue.append(current_path + [neighbor])
        return []


    def assign_paths(self):
        start = self.map.start_hub
        end = self.map.end_hub
        for drone in self.drones:
            drone.path = self.find_path(start, end)
            if drone.path == None:
                raise ValueError("[ENGINE ERROR]: Connetion doesn't exist!")
            drone.path_index = 1


    def run_turn(self) -> str:
        intensions = {}
        for drone in self.drones:
            if drone.delivered is False:
                if drone.path_index >= len(drone.path):
                    drone.delivered = True
                    continue
                target_hub = drone.path[drone.path_index]
                intensions[drone] = target_hub

        hub_intensions = {}
        for drone, hub in intensions.items():
            if hub not in hub_intensions:
                hub_intensions[hub] = []
            hub_intensions[hub].append(drone)
        
        approved = {}
        for hub, drones_list in hub_intensions.items():
            free_space = hub.capacity - len(hub.drones)
            
            for drone in drones_list[:free_space]:
                approved[drone] = hub
        
        for drone, target_hub in approved.items():
            if target_hub.accept_drone(drone.drone_id):
                if drone.drone_id in drone.location.drones:
                    drone.location.release_drone(drone.drone_id)
                
                drone.location = target_hub
                drone.path_index += 1
            
                if target_hub == self.map.end_hub:
                    drone.delivered = True
        
        self.turn += 1
        moves = [f"{drone.name}-{hub.name}" for drone, hub in approved.items()]
        log_msg = " ".join(moves)
        self.log.append(log_msg)

    def run_all(self) -> list[str]:
        self.assign_paths()
        max_turns = 100
        while not all(drone.delivered for drone in self.drones) and self.turn < max_turns:
            self.run_turn()
        if self.turn >= max_turns:
            print(f"[WARNING] Dosáhli jsme limitu {max_turns} tahů!")
        return self.log
