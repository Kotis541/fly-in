import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from Backend.graph import Map
from Backend.engine import Engine
from typing import Any



pygame.init()

WHITE = (255, 255, 255)
GREEN = (126, 217, 87)
ANIMATION_SPEED = 0.016


class Visualizer:
    """Handles the Pygame-based graphical interface for animating the
    drone delivery simulation.
    """
    def __init__(self, map: Map, engine: Engine) -> None:
        """Initializes the Pygame visualizer with the map and simulation
        engine.
        """
        self.map = map
        self.engine = engine

        # Pygame setup
        self.info = pygame.display.Info()
        self.screen = self._create_screen()

        # Load drone image
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            icon_path = os.path.join(script_dir, "image/drone.png")
            self.drone_img = pygame.image.load(icon_path)
        except (FileNotFoundError, pygame.error):
            print("[ERROR - Visualizer]: Can't load drone img")
            exit(1)
        self.drone = pygame.transform.scale(self.drone_img, (40, 20))
        pygame.display.set_caption("Fly-In Visualization")

        # Animation state
        self.visual_drones: dict[str, dict[str, Any]] = {}
        self.current_turn = 0
        self.turn_progress = 0.0
        self.step_in_progress = False
        self.auto_mode = False
        self.running = True

        # Fonts
        self.font = pygame.font.SysFont("Arial", 15)
        self.font2 = pygame.font.SysFont("Arial", 18)

        self._init_visual_drones()

    def _create_screen(self) -> pygame.Surface:
        """Creates and returns the Pygame display surface based on map
        dimensions.
        """
        req_w = len(self.map.hubs) * 120
        req_h = len(self.map.hubs) * 50
        win_w = self.info.current_w
        win_h = self.info.current_h

        if req_w > win_w or req_h > win_h:
            return pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
        return pygame.display.set_mode((req_w, req_h), pygame.RESIZABLE)

    def _init_visual_drones(self) -> None:
        """Sets up the initial visual state and target nodes for all drones."""
        for drone_ in self.engine.drones:
            self.visual_drones[drone_.name] = {
                'current_node': self.map.start_hub,
                'target_node': self.map.start_hub
            }
        if len(self.engine.visual_log) > 0:
            for move in self.engine.visual_log[0].split():
                d_name, h_name = move.split("-")
                self.visual_drones[d_name]['target_node'] = \
                    self.map.hubs[h_name]

    def run(self) -> None:
        """Starts the main Pygame event and rendering loop."""
        clock = pygame.time.Clock()

        while self.running:
            events = pygame.event.get()
            clock.tick(60)
            mouse_pos = pygame.mouse.get_pos()

            self._handle_events(events)
            self._update()
            self._draw(mouse_pos)

    def _handle_events(self, events: list[pygame.event.Event]) -> None:
        """Processes user input events such as quitting and mouse clicks."""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_click(event.pos)

    def _handle_click(self, pos: tuple[int, int]) -> None:
        """Handles mouse clicks on the interface buttons."""
        rect_step = pygame.Rect(10, 10, 80, 30)
        rect_auto = pygame.Rect(100, 10, 80, 30)
        rect_reset = pygame.Rect(190, 10, 80, 30)

        if rect_auto.collidepoint(pos):
            self.auto_mode = not self.auto_mode
        elif rect_step.collidepoint(pos):
            self.step_in_progress = True
        elif rect_reset.collidepoint(pos):
            self._reset()

    def _reset(self) -> None:
        """Resets the visualization back to the first turn."""
        self.current_turn = 0
        self.turn_progress = 0.0
        self.step_in_progress = False
        self.auto_mode = False
        self._init_visual_drones()

    def _update(self) -> None:
        """Advances the animation and updates turn progress."""
        if ((self.step_in_progress or self.auto_mode) and
                self.current_turn < len(self.engine.visual_log)):
            self.turn_progress += ANIMATION_SPEED
            if self.turn_progress >= 1.0:
                for d_name in self.visual_drones:
                    d_info = self.visual_drones[d_name]
                    d_info['current_node'] = d_info['target_node']

                self.current_turn += 1
                self.turn_progress = 0.0
                self.step_in_progress = False

                if self.current_turn < len(self.engine.visual_log):
                    self._update_drone_targets()
                else:
                    self.auto_mode = False

    def _update_drone_targets(self) -> None:
        """Updates the destination hubs for drones based on the
        simulation log.
        """
        moves = self.engine.visual_log[self.current_turn].split()
        moved_drones = {}
        for m in moves:
            d_name, h_name = m.split("-")
            moved_drones[d_name] = h_name

        for d_name in self.visual_drones:
            if d_name in moved_drones:
                target = self.map.hubs[moved_drones[d_name]]
                self.visual_drones[d_name]['target_node'] = target
            else:
                curr = self.visual_drones[d_name]['current_node']
                self.visual_drones[d_name]['target_node'] = curr

    def _draw(self, mouse_pos: tuple[int, int]) -> None:
        """Renders all visual elements onto the screen."""
        screen_w, screen_h = self.screen.get_size()
        self.screen.fill(WHITE)
        pygame.draw.rect(self.screen, (235, 235, 235),
                         [-10, -10, 420, 60], border_radius=10)

        self._draw_buttons(mouse_pos)
        self._draw_turn_counter()
        self._draw_connections(screen_w, screen_h)
        self._draw_hubs(screen_w, screen_h)
        self._draw_drones(screen_w, screen_h)

        pygame.display.flip()

    def _draw_buttons(self, mouse_pos: tuple[int, int]) -> None:
        """Draws the control buttons (STEP, AUTO, RESET)."""
        rect_step = pygame.Rect(10, 10, 80, 30)
        rect_auto = pygame.Rect(100, 10, 80, 30)
        rect_reset = pygame.Rect(190, 10, 80, 30)

        # Step button
        c_step = (170, 170, 170) if rect_step.collidepoint(
            mouse_pos) else (200, 200, 200)
        pygame.draw.rect(self.screen, c_step, rect_step, border_radius=6)
        txt_step = self.font2.render("STEP", True, 'black')
        self.screen.blit(txt_step,
                         txt_step.get_rect(center=rect_step.center)
                         )

        # Auto button
        c_auto = ((80, 180, 80) if self.auto_mode
                  else (170, 170, 170) if rect_auto.collidepoint(mouse_pos)
                  else (200, 200, 200))
        pygame.draw.rect(self.screen, c_auto, rect_auto, border_radius=6)
        txt_auto = self.font2.render("AUTO", True, 'black')
        self.screen.blit(txt_auto,
                         txt_auto.get_rect(center=rect_auto.center)
                         )

        # Reset button
        c_reset = (170, 170, 170) if rect_reset.collidepoint(
            mouse_pos) else (200, 200, 200)
        pygame.draw.rect(self.screen, c_reset, rect_reset, border_radius=6)
        txt_reset = self.font2.render("RESET", True, 'black')
        self.screen.blit(txt_reset,
                         txt_reset.get_rect(center=rect_reset.center)
                         )

    def _draw_turn_counter(self) -> None:
        """Displays the current turn number out of the total turns."""
        turn_text = f"Turn: {self.current_turn} / \
{len(self.engine.visual_log)}"
        txt_step_nb = self.font2.render(turn_text, True, 'black')
        rect_step_nb = txt_step_nb.get_rect(topleft=(290, 15))
        self.screen.blit(txt_step_nb, rect_step_nb)

    def _draw_connections(self, screen_w: int, screen_h: int) -> None:
        """Renders the connection lines between hubs."""
        drawn_connections = set()
        for hub_name, hub in self.map.hubs.items():
            for conn in hub.connections:
                conn_names = (conn.node_a.name, conn.node_b.name)
                conn_id = tuple(sorted(conn_names))
                if conn_id not in drawn_connections:
                    drawn_connections.add(conn_id)
                    start_pos = self.engine.coord_scale(
                        conn.node_a.x, conn.node_a.y, screen_w, screen_h)
                    end_pos = self.engine.coord_scale(
                        conn.node_b.x, conn.node_b.y, screen_w, screen_h)
                    pygame.draw.line(
                        self.screen, (150, 150, 150), start_pos, end_pos, 3)

    def _draw_hubs(self, screen_w: int, screen_h: int) -> None:
        """Draws the map hubs and their names."""
        for hub in self.map.hubs:
            hub_obj = self.map.hubs[hub]
            x, y = self.engine.coord_scale(
                hub_obj.x, hub_obj.y, screen_w, screen_h)
            try:
                color = pygame.Color(hub_obj.color) if hub_obj.color else (0, 150, 255)
            except ValueError:
                color = (0, 150, 255)
            pygame.draw.circle(self.screen, color, (x, y), 20, 0)
            name = self.font.render(hub, True, (0, 0, 0))
            self.screen.blit(name, (x + 20, y + 10))

    def _draw_drones(self, screen_w: int, screen_h: int) -> None:
        """Renders the drones interpolating between their current and
        target nodes.
        """
        for d_name, d_info in self.visual_drones.items():
            curr_node = d_info['current_node']
            target_node = d_info['target_node']
            start_x, start_y = self.engine.coord_scale(
                curr_node.x, curr_node.y, screen_w, screen_h)
            end_x, end_y = self.engine.coord_scale(
                target_node.x, target_node.y, screen_w, screen_h)
            flight_progress = min(self.turn_progress / 0.8, 1)

            current_x = start_x + (end_x - start_x) * flight_progress
            current_y = start_y + (end_y - start_y) * flight_progress

            self.screen.blit(self.drone, (current_x - 20, current_y - 10))
