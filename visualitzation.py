import pygame
from classes import *
from engine import Engine
import math
from typing import Tuple

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
    
    if len(engine.visual_log) > 0:
        for move in engine.visual_log[0].split():
            d_name, h_name = move.split("-")
            visual_drones[d_name]['target_node'] = map.hubs[h_name]

    clock = pygame.time.Clock()
    current_turn = 0
    turn_progress = 0.0
    running = True
    font = pygame.font.SysFont("Arial", 15)
    font2 = pygame.font.SysFont("Arial", 18)
    auto_mode = False

    while running:
        clock.tick(60)

        screen_w, screen_h = screen.get_size()
        txt_step = font2.render(" STEP ", True, 'black')
        txt_auto = font2.render(" AUTO ", True, 'black')
        rect_step = txt_step.get_rect(topleft=(10,10))
        rect_auto = txt_auto.get_rect(topleft=(100, 10))
        
        if current_turn < len(engine.visual_log):
            turn_progress += ANIMATION_SPEED
            if turn_progress >= 1.0:
                current_turn += 1
                
                for d_name in visual_drones:
                    visual_drones[d_name]['current_node'] = visual_drones[d_name]['target_node']
                
                if current_turn < len(engine.visual_log):
                    moves = engine.visual_log[current_turn].split()
                    moved_drones = {m.split("-")[0]: m.split("-")[1] for m in moves}
                    
                    for d_name in visual_drones:
                        if d_name in moved_drones:
                            visual_drones[d_name]['target_node'] = map.hubs[moved_drones[d_name]]
                        else:
                            visual_drones[d_name]['target_node'] = visual_drones[d_name]['current_node']
                            
                if current_turn < len(engine.visual_log):
                    turn_progress -= 1.0
                else:
                    turn_progress = 1.0
                    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if rect_auto.collidepoint(event.pos):
                        auto_mode = not auto_mode
                    elif rect_step.collidepoint(event.pos):
                        if current_turn < len(engine.visual_log):
                            current_turn += 1
                            turn_progress = 0.0
        if auto_mode and current_turn >= len(engine.visual_log):
            auto_mode = False

        screen.fill(WHITE) 
        screen.blit(txt_step, rect_step)
        pygame.draw.rect(screen, (255, 0, 0), rect_step, 1)
        screen.blit(txt_auto, rect_auto)
        pygame.draw.rect(screen, (255, 0, 0), rect_auto, 1)
       
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
            # Names of Hubs
            name = font.render(hub, True, (0,0,0))
            screen.blit(name, (x + 20, y + 10))
        
        # Animation of drones
        for d_name, d_info in visual_drones.items():
            start_x, start_y = engine.coord_scale(d_info['current_node'].x, d_info['current_node'].y, screen_w, screen_h)
            end_x, end_y = engine.coord_scale(d_info['target_node'].x, d_info['target_node'].y, screen_w, screen_h)
            flight_progress = min(turn_progress / 0.8, 1)

            current_x = start_x + (end_x - start_x) * flight_progress
            current_y = start_y + (end_y - start_y) * flight_progress

            screen.blit(drone, (current_x - 20, current_y - 10))

        pygame.display.flip()

    pygame.quit()
