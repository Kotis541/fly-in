from Backend.parser import Parser
from Backend.engine import Engine
from Frontend.display import Visualizer
import sys


def main() -> None:
    """Runs the main simulation loop and launches the Pygame visualizer."""
    try:
        map_obj, drones = Parser.parse_file(sys.argv[1])
        if len(sys.argv) > 2:
            raise ValueError("Cannot add more files!")
    except (FileNotFoundError, ValueError) as e:
        print(e)
        exit()
    engine = Engine(map_obj, drones)
    log = engine.run_simulation()
    for line in log:
        print(line)
    try:
        visualizer = Visualizer(map_obj, engine)
        visualizer.run()
    except KeyboardInterrupt:
        print("Thanks for using Fly - in")

if __name__ == "__main__":
    main()
