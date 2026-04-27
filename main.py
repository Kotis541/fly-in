from Backend.parser import Parser
from Backend.engine import Engine
from Frontend.display import Visualizer
import sys


def main() -> None:
    """Runs the main simulation loop and launches the Pygame visualizer."""
    if len(sys.argv) < 2:
        print("[ERROR]: Usage: python3 main.py <map_file>")
        exit(1)
    if len(sys.argv) > 2:
        print("[ERROR]: Too many arguments. Usage: python main.py <map_file>")
        exit(1)
    try:
        map_obj, drones = Parser.parse_file(sys.argv[1])
        engine = Engine(map_obj, drones)
        log = engine.run_simulation()
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(e)
        exit(1)
    except Exception as e:
        print(f"[FATAL ERROR]: An unexpected failure occurred: {e}")
        exit(1)
    for line in log:
        print(line)
    try:
        visualizer = Visualizer(map_obj, engine)
        visualizer.run()
    except KeyboardInterrupt:
        print("Thanks for using Fly - in")


if __name__ == "__main__":
    main()
