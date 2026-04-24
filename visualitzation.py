import pygame
from classes import *
from engine import Engine
import math

pygame.init()

WHITE = (255,255,255)
GREEN = (126, 217, 87)
ANIMATION_SPEED = 0.016

def visualization(map: Map, engine: Engine):
    info = pygame.display.Info()
    monitor_w = info.current_w
    monitor_h = info.current_h

    req_w = len(map.hubs) * 100
    req_h = len(map.hubs) * 30
    if req_w > monitor_w or req_h > monitor_h:
        screen = pygame.display.set_mode((monitor_w, monitor_h), pygame.RESIZABLE)
    else:
        screen = pygame.display.set_mode((req_w, req_h), pygame.RESIZABLE)
    image = pygame.image.load(r's.png')
    drone = pygame.transform.scale(image, (40, 20))
    pygame.display.set_caption("Fly-In Visualization")
    
    visual_drones = {}
    for drone_ in engine.drones:
        visual_drones[drone_.name] = {'current_node': map.start_hub, 'target_node': map.start_hub}
    
    # Analyzátor doporučuje: Načti cíle pro vůbec první tah (Tah 0) ještě před startem animace
    if len(engine.visual_log) > 0:
        for move in engine.visual_log[0].split():
            d_name, h_name = move.split("-")
            visual_drones[d_name]['target_node'] = map.hubs[h_name]

    clock = pygame.time.Clock()
    current_turn = 0
    turn_progress = 0.0
    running = True
    while running:
        clock.tick(60)
        
        if current_turn < len(engine.visual_log):
            turn_progress += ANIMATION_SPEED
            if turn_progress >= 1.0:
                current_turn += 1
                
                # 1. Zafixování doletu (posuneme cíl do startu nového tahu)
                for d_name in visual_drones:
                    visual_drones[d_name]['current_node'] = visual_drones[d_name]['target_node']
                
                # 2. Vyčtení nového tahu (pokud nejsme na konci logu)
                if current_turn < len(engine.visual_log):
                    moves = engine.visual_log[current_turn].split()
                    # Uděláme si šikovný dočasný slovník s pohyby: {'D1': 'HubA', 'D2': 'HubB'}
                    moved_drones = {m.split("-")[0]: m.split("-")[1] for m in moves}
                    
                    for d_name in visual_drones:
                        if d_name in moved_drones:
                            # Vyhledáme konkrétní objekt Hubu z mapy podle stringu
                            visual_drones[d_name]['target_node'] = map.hubs[moved_drones[d_name]]
                        else:
                            # Tento dron v tomto tahu nikam neletí
                            visual_drones[d_name]['target_node'] = visual_drones[d_name]['current_node']
                            
                if current_turn < len(engine.visual_log):
                    turn_progress -= 1.0
                else:
                    turn_progress = 1.0
                    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)

        screen_w, screen_h = screen.get_size()
        
        # Vizualization of Connections
        drawn_connections = set()
        for hub_name, hub in map.hubs.items():
            for conn in hub.connections:
                conn_id = tuple(sorted([conn.node_a.name, conn.node_b.name]))
                if conn_id not in drawn_connections:
                    drawn_connections.add(conn_id)
                    start_pos = engine.coord_scale(conn.node_a.x, conn.node_a.y, screen_w, screen_h)
                    end_pos = engine.coord_scale(conn.node_b.x, conn.node_b.y, screen_w, screen_h)
                    pygame.draw.line(screen, (150, 150, 150), start_pos, end_pos, 3)

        # Vizualization of hubs
        for i, hub in enumerate(map.hubs):
            x, y = engine.coord_scale(map.hubs[hub].x, map.hubs[hub].y, screen_w, screen_h)
            color = map.hubs[hub].color if map.hubs[hub].color else (0, 150, 255)
            pygame.draw.circle(screen, color, (x, y), 20, 0)
        
        # Animace dronů pomocí lineární interpolace (Lerp)
        for d_name, d_info in visual_drones.items():
            # 1. Získání pixelových souřadnic startu a cíle pro aktuální tah
            start_x, start_y = engine.coord_scale(d_info['current_node'].x, d_info['current_node'].y, screen_w, screen_h)
            end_x, end_y = engine.coord_scale(d_info['target_node'].x, d_info['target_node'].y, screen_w, screen_h)
            flight_progress = min(turn_progress /  0.8, 1)
            # 2. Lerp - výpočet aktuální pozice mezi startem a cílem
            current_x = start_x + (end_x - start_x) * flight_progress
            current_y = start_y + (end_y - start_y) * flight_progress
            
            # 3. Vykreslení (s posunem o polovinu velikosti obrázku, aby byl vycentrovaný)
            screen.blit(drone, (current_x - 20, current_y - 10))
            
        pygame.display.flip()

    pygame.quit()
