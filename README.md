# Fly-In - Drone Routing Simulation

*This project has been created as part of the 42 curriculum by vokotera.*

## Description
 This project, is a drone routing simulation dessigned to navigate drones from a starting hub to ending hub through a network of connected zones. The primary goal is to minimize total number of simulation turns and respect capacity of hubs and connections.

The system handles various zone types:
- **Normal zones**: Standard movement (1-turn cost)
- **Restricted zones**: Slow passage (2-turn cost)
- **Priority zones**: High priority routing
- **Blocked zones**: Blocked areas

## Instructions
 To set up and run the simulation, user the following Makefile command:
```bash
make install    # Install dependencies (Pygame, MyPy, flake8)
make run        # Run the simulation
make lint       # Check code quality (flake8 + mypy)
make debug      # Debug mode with pdb
make clean      # Remove cache files
```
### Map
Maps are defined in .txt files with the following syntax:

```
nb_drones: 5

start_hub: A 0 0 [zone=normal color=green]
hub: B 100 50 [zone=restricted max_drones=3]
hub: C 200 50 [zone=blocked]
end_hub: D 300 0 [zone=normal]

connection: A-B [max_link_capacity=2]
connection: B-D [max_link_capacity=5]
connection: C-D [max_link_capacity=3]
```
#### Metadata Options
- Hubs: zone, color, max_drones
- Connections: max_link_capacity

## Algorithm and Implementation
Uses Dijkstra's Algorithm to compute shortest weighted paths:

- Normal zones: cost = 1
- Restricted zones: cost = 2
- Blocked zones: cost = ∞

A drone only takes a step forward if there is physical capacity on both the connection and the destination zone. If the path is blocked, the drone safely waits in its current hub and skips a turn.

## Visual Interface
Built with Pygame, featuring:

#### Controls
- STEP: Advance simulation by 1 turn
- AUTO: Run simulation continuously
- RESET: Return to initial state

#### Display
- Hubs rendered as colored circles
- Connections as gray lines
- Drones animated in flight
- Turn counter display

## Resources
[Pygame - geeks for geeks](https://www.geeksforgeeks.org/python/introduction-to-pygame/)

[Dijkstra's Algorithm](https://www.geeksforgeeks.org/dsa/dijkstras-shortest-path-algorithm-greedy-algo-7/)

Other


### Ai usage
Artificial Intelligence was utilized during the development of this project for the following tasks:
 - Planning - Structural organization of the simulation engine and class hierarchy.
 - Optimization - Refining the Dijkstra implementation for better performance

 **AI was not used for blind copy-pasting; all logic was reviewed, understood, and manually integrated**