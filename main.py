from parser import parse_file
from engine import Engine
from visualitzation import visualization


def test_parser():
    # """Testuje parse_file na test.txt"""
    # try:
    #     map_obj, drones = parse_file("test.txt")
    # except ValueError as e:
    #     print(e)
    #     return
    
    # # Test 1: Check hubs count
    # assert len(map_obj.hubs) == 7, f"Mělo být 7 hubů, je {len(map_obj.hubs)}"
    # print("✓ Počet hubů: 7")
    
    # # Test 2: Check start_hub
    # assert map_obj.start_hub is not None, "start_hub je None"
    # assert map_obj.start_hub.name == "hub", f"start_hub jméno: {map_obj.start_hub.name}"
    # assert map_obj.start_hub.x == 0 and map_obj.start_hub.y == 0, "start_hub souřadnice"
    # print("✓ start_hub (hub) OK")
    
    # # Test 3: Check end_hub
    # assert map_obj.end_hub is not None, "end_hub je None"
    # assert map_obj.end_hub.name == "goal", f"end_hub jméno: {map_obj.end_hub.name}"
    # assert map_obj.end_hub.x == 10 and map_obj.end_hub.y == 10, "end_hub souřadnice"
    # print("✓ end_hub (goal) OK")
    
    # # Test 4: Check drones
    # assert len(drones) == 5, f"Mělo být 5 dronů, je {len(drones)}"
    # print("✓ Počet dronů: 5")
    
    # # Test 5: Check connections
    # assert len(map_obj.hubs["hub"].connections) > 0, "hub nema connections"
    # assert len(map_obj.hubs["goal"].connections) > 0, "goal nema connections"
    # print("✓ Connections mapovány správně")
    
    # print("\n✅ Všechny testy prošly!")

    print("=== TEST ENGINE === ")

    map_obj, drones = parse_file("maps/easy/01_linear_path.txt")
    engine = Engine(map_obj, drones)
    log = engine.run_simulation()
    for line in log:
        print(line)
    print(f"Hotovo za {engine.turn} tahů")
    visualization(map_obj)

    for d in engine.drones:
        print(d.name, [h.name for h in d.path])
    

if __name__ == "__main__":
    test_parser()