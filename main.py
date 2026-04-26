from Backend.parser import Parser
from Backend.engine import Engine
from Frontend.display import Visualizer


def main() -> None:
    """Runs the main simulation loop and launches the Pygame visualizer."""
    try:
        map_obj, drones = Parser.parse_file("maps/hard/03_ultimate_challenge.txt")
    except FileNotFoundError:
        print("File not exists!")
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
