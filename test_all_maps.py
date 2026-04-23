#!/usr/bin/env python3
"""Test all maps and check performance against benchmarks"""

from parser import parse_file
from engine import Engine
import os

BENCHMARKS = {
    "easy": {
        "01_linear_path.txt": 6,
        "02_simple_fork.txt": 6,
        "03_basic_capacity.txt": 8,
    },
    "medium": {
        "01_dead_end_trap.txt": 15,
        "02_circular_loop.txt": 20,
        "03_priority_puzzle.txt": 12,
    },
    "hard": {
        "01_maze_nightmare.txt": 45,
        "02_capacity_hell.txt": 60,
        "03_ultimate_challenge.txt": 35,
    },
    "challenger": {
        "01_the_impossible_dream.txt": 45,
    }
}

def test_map(filepath, expected_turns):
    """Test a single map"""
    try:
        map_obj, drones = parse_file(filepath)
        engine = Engine(map_obj, drones)
        log = engine.run_simulation()
        
        actual_turns = engine.turn
        status = "✓" if actual_turns <= expected_turns else "✗"
        
        print(f"{status} {os.path.basename(filepath):40} Expected: {expected_turns:3}, Got: {actual_turns:3}, Drones: {len(drones)}")
        
        return actual_turns <= expected_turns
    except Exception as e:
        print(f"✗ {os.path.basename(filepath):40} ERROR: {str(e)}")
        return False

def main():
    print("=" * 90)
    print("TESTING ALL MAPS")
    print("=" * 90)
    
    results = {}
    
    for difficulty, maps in BENCHMARKS.items():
        print(f"\n{difficulty.upper()} MAPS (target ≤ X turns)")
        print("-" * 90)
        
        passed = 0
        total = len(maps)
        
        for map_name, expected_turns in maps.items():
            map_path = f"maps/{difficulty}/{map_name}"
            if test_map(map_path, expected_turns):
                passed += 1
        
        results[difficulty] = (passed, total)
        print(f"  Result: {passed}/{total} maps passed")
    
    print("\n" + "=" * 90)
    print("SUMMARY")
    print("=" * 90)
    
    total_passed = sum(p for p, _ in results.values())
    total_maps = sum(t for _, t in results.values())
    
    for difficulty, (passed, total) in results.items():
        print(f"{difficulty:15} {passed}/{total}")
    
    print(f"\nTotal: {total_passed}/{total_maps} maps passed")
    
    if total_passed == total_maps:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n❌ {total_maps - total_passed} maps failed benchmark")

if __name__ == "__main__":
    main()
