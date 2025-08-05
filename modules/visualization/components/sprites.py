"""Sprite management for Wumpus World entities."""

import pygame
import math
import modules.visualization.ui_config as config
from ...utils import Orientation


class SpriteManager:
    """Manages drawing of game entities and effects."""

    def __init__(self, cell_size):
        """Initialize sprite manager with cell size."""
        self.cell_size = cell_size
        self.font = None
        self.angle_map = {
            Orientation.NORTH: -math.pi / 2,
            Orientation.EAST: 0,
            Orientation.SOUTH: math.pi / 2,
            Orientation.WEST: math.pi,
        }

    def init_font(self):
        """Initialize pygame font."""
        if not pygame.get_init():
            return
        self.font = pygame.font.Font(None, self.cell_size // 3)

    def draw_gold(self, surface, x, y):
        """Draw gold as a yellow diamond."""
        center_x = x + self.cell_size // 2
        center_y = y + self.cell_size // 2
        size = self.cell_size // 4

        points = [
            (center_x, center_y - size),  # Top
            (center_x + size, center_y),  # Right
            (center_x, center_y + size),  # Bottom
            (center_x - size, center_y),  # Left
        ]
        pygame.draw.polygon(surface, config.entity["gold"], points)

    def draw_wumpus(self, surface, x, y, alive=True):
        """Draw wumpus as a brown circle."""
        center_x = x + self.cell_size // 2
        center_y = y + self.cell_size // 2
        radius = self.cell_size // 3

        pygame.draw.circle(
            surface, config.entity["wumpus"], (center_x, center_y), radius
        )

        # Draw eyes
        eye_offset = radius // 3
        eye_radius = 3
        pygame.draw.circle(
            surface,
            config.colors["black"],
            (center_x - eye_offset, center_y - eye_offset),
            eye_radius,
        )
        pygame.draw.circle(
            surface,
            config.colors["black"],
            (center_x + eye_offset, center_y - eye_offset),
            eye_radius,
        )

        if not alive:
            # Draw X for dead wumpus
            pygame.draw.line(
                surface,
                config.colors["red"],
                (center_x - radius // 2, center_y - radius // 2),
                (center_x + radius // 2, center_y + radius // 2),
                3,
            )
            pygame.draw.line(
                surface,
                config.colors["red"],
                (center_x + radius // 2, center_y - radius // 2),
                (center_x - radius // 2, center_y + radius // 2),
                3,
            )

    def draw_pit(self, surface, x, y):
        """Draw pit as a dark square."""
        size = self.cell_size * 0.4
        left = x + self.cell_size // 2 - size
        top = y + self.cell_size // 2 - size

        width = size * 2
        height = size * 2

        pygame.draw.rect(
            surface,
            config.entity["pit"],
            (left, top, width, height),
            border_radius=4,
        )

    def __draw_orientation_arrow(
        self, surface, agent_size, center_x, center_y, orientation
    ):
        """Draw directional arrow for the agent."""
        triangle_distance = agent_size * 1.2
        triangle_size = agent_size * 0.5

        if orientation in self.angle_map:
            angle = self.angle_map[orientation]

            triangle_center_x = center_x + int(triangle_distance * math.cos(angle))
            triangle_center_y = center_y + int(triangle_distance * math.sin(angle))

            tip_x = triangle_center_x + int(triangle_size * math.cos(angle))
            tip_y = triangle_center_y + int(triangle_size * math.sin(angle))

            base_angle1 = angle + math.pi / 2
            base_angle2 = angle - math.pi / 2

            base1_x = triangle_center_x + int(
                (triangle_size * 0.6) * math.cos(base_angle1)
            )
            base1_y = triangle_center_y + int(
                (triangle_size * 0.6) * math.sin(base_angle1)
            )
            base2_x = triangle_center_x + int(
                (triangle_size * 0.6) * math.cos(base_angle2)
            )
            base2_y = triangle_center_y + int(
                (triangle_size * 0.6) * math.sin(base_angle2)
            )

            triangle_points = [(tip_x, tip_y), (base1_x, base1_y), (base2_x, base2_y)]
            pygame.draw.polygon(surface, config.entity["agent"], triangle_points)

    def __draw_gold_indicator(self, surface, center_x, center_y):
        """Draw gold indicator on the agent."""
        gold_size = self.cell_size // 5
        gold_center_x = center_x
        gold_center_y = center_y

        points = [
            (gold_center_x, gold_center_y - gold_size // 2),  # Top
            (gold_center_x + gold_size // 2, gold_center_y),  # Right
            (gold_center_x, gold_center_y + gold_size // 2),  # Bottom
            (gold_center_x - gold_size // 2, gold_center_y),  # Left
        ]
        pygame.draw.polygon(surface, config.entity["gold"], points)

    def __draw_shoot_arrow(self, surface, agent_size, center_x, center_y, orientation):
        """Draw indicator of a arrow shot by the agent."""
        triangle_distance = agent_size * 0.7
        triangle_size = agent_size * 0.3

        if orientation in self.angle_map:
            angle = self.angle_map[orientation]

            start_distance = agent_size * 0.7
            start_x = center_x + int(start_distance * math.cos(angle))
            start_y = center_y + int(start_distance * math.sin(angle))

            end_distance = agent_size * 0.7
            end_x = center_x - int(end_distance * math.cos(angle))
            end_y = center_y - int(end_distance * math.sin(angle))

            pygame.draw.line(
                surface,
                config.entity["arrow_body"],
                (start_x, start_y),
                (end_x, end_y),
                3,
            )

            triangle_center_x = center_x + int(triangle_distance * math.cos(angle))
            triangle_center_y = center_y + int(triangle_distance * math.sin(angle))

            tip_x = triangle_center_x + int(triangle_size * math.cos(angle))
            tip_y = triangle_center_y + int(triangle_size * math.sin(angle))

            base_angle1 = angle + math.pi / 2
            base_angle2 = angle - math.pi / 2

            base1_x = triangle_center_x + int(triangle_size * math.cos(base_angle1))
            base1_y = triangle_center_y + int(triangle_size * math.sin(base_angle1))
            base2_x = triangle_center_x + int(triangle_size * math.cos(base_angle2))
            base2_y = triangle_center_y + int(triangle_size * math.sin(base_angle2))

            triangle_points = [(tip_x, tip_y), (base1_x, base1_y), (base2_x, base2_y)]
            pygame.draw.polygon(surface, config.entity["arrow_head"], triangle_points)

    def __draw_scream_indicator(self, surface, center_x, center_y):
        """Draw wumpus scream indicator for the agent."""
        if not self.font:
            self.init_font()

        scream_x = center_x - self.cell_size // 2 + self.cell_size // 5
        scream_y = center_y - self.cell_size // 2 + self.cell_size // 5

        # Vẽ 3 dấu chấm than màu đỏ
        if self.font:
            scream_text = self.font.render("!!!", True, config.colors["red"])
            surface.blit(scream_text, (scream_x, scream_y))
        else:
            # Fallback nếu không có font: vẽ 3 hình tròn nhỏ
            for i in range(3):
                pygame.draw.circle(
                    surface, config.colors["red"], (scream_x + i * 6, scream_y + 5), 2
                )

    def draw_agent(
        self,
        surface,
        x,
        y,
        orientation,
        has_gold=False,
        is_alive=True,
        shoot_arrow=False,
        hear_scream=False,
    ):
        """Draw agent with directional arrow and optional gold indicator."""
        center_x = x + self.cell_size // 2
        center_y = y + self.cell_size // 2
        size = self.cell_size // 4

        pygame.draw.circle(surface, config.entity["agent"], (center_x, center_y), size)

        # Draw red X over dead agent
        if not is_alive:
            pygame.draw.line(
                surface,
                config.colors["red"],
                (center_x - size // 2, center_y - size // 2),
                (center_x + size // 2, center_y + size // 2),
                3,
            )
            pygame.draw.line(
                surface,
                config.colors["red"],
                (center_x + size // 2, center_y - size // 2),
                (center_x - size // 2, center_y + size // 2),
                3,
            )

        # Draw orientation arrow
        self.__draw_orientation_arrow(surface, size, center_x, center_y, orientation)

        # Draw gold indicator
        if has_gold:
            self.__draw_gold_indicator(surface, center_x, center_y)

        # Draw arrow if the agent has shot it
        if shoot_arrow:
            self.__draw_shoot_arrow(surface, size, center_x, center_y, orientation)

        # Draw scream indicator if the agent heard a scream
        if hear_scream:
            self.__draw_scream_indicator(surface, center_x, center_y)

    def draw_breeze(self, surface, x, y):
        """Draw breeze effect as curved lines."""
        center_x = x + self.cell_size // 2
        center_y = y + self.cell_size // 2

        # Draw wavy lines to represent wind
        for i in range(3):
            offset = (i - 1) * 8
            start_x = x + 10
            end_x = x + self.cell_size - 10
            y_pos = center_y + offset

            points = []
            for px in range(start_x, end_x, 4):
                wave_y = y_pos + int(3 * math.sin((px - start_x) * 0.3))
                points.append((px, wave_y))

            if len(points) > 1:
                pygame.draw.lines(surface, config.entity["breeze"], False, points, 2)

    def draw_stench(self, surface, x, y):
        """Draw stench effect as wavy lines."""
        center_x = x + self.cell_size // 2
        center_y = y + self.cell_size // 2

        # Draw stench as red wavy lines going up
        for i in range(4):
            offset_x = (i - 1.5) * 6
            start_y = y + self.cell_size - 10
            end_y = y + 10

            points = []
            for py in range(start_y, end_y, -3):
                wave_x = center_x + offset_x + int(4 * math.sin((start_y - py) * 0.2))
                points.append((wave_x, py))

            if len(points) > 1:
                pygame.draw.lines(surface, config.entity["stench"], False, points, 2)
