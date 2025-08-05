import pygame
import modules.visualization.ui_config as config
from modules.visualization.components.sprites import SpriteManager


class Cell:
    """A class to represent a cell on the board"""

    def __init__(self, row, col, cell_size, sprite_manager: SpriteManager):
        """Initialize a new tile"""
        self.position = (
            col * cell_size,
            row * cell_size,
        )
        self.size = cell_size
        self.color = config.cell["default"]
        self.border_color = config.cell["border"]
        self.border_size = cell_size * 0.02
        self.sprite_manager = sprite_manager

    def draw(self, position: tuple[int, int], surface: pygame.Surface):
        """Draw the cell on the given surface"""
        outside_rect = pygame.Rect(
            position[0] + self.position[0],
            position[1] + self.position[1],
            self.size,
            self.size,
        )

        pygame.draw.rect(
            surface,
            self.border_color,
            outside_rect,
        )

        inside_rect = pygame.Rect(
            position[0] + self.position[0] + self.border_size,
            position[1] + self.position[1] + self.border_size,
            self.size - 2 * self.border_size,
            self.size - 2 * self.border_size,
        )

        pygame.draw.rect(
            surface,
            self.color,
            inside_rect,
        )

    def set_cell_type(self, type: str):
        """Set the type of the cell"""
        self.color = config.cell[type]

    def draw_entity(
        self,
        position: tuple[int, int],
        surface: pygame.Surface,
        entity_data,
    ):
        if entity_data.get("name") == "Pit":
            self.sprite_manager.draw_pit(
                surface,
                int(position[0] + self.position[0]),
                int(position[1] + self.position[1]),
            )
        elif entity_data.get("name") == "Wumpus":
            if properties := entity_data.get("properties"):
                self.sprite_manager.draw_wumpus(
                    surface,
                    int(position[0] + self.position[0]),
                    int(position[1] + self.position[1]),
                    not properties.get("screamed", False),
                )
            else:
                self.sprite_manager.draw_wumpus(
                    surface,
                    int(position[0] + self.position[0]),
                    int(position[1] + self.position[1]),
                    True,
                )
        elif entity_data.get("name") == "Agent":
            # Use agent_info passed as entity_data
            if properties := entity_data.get("properties"):
                orientation = properties.get("orientation", "EAST")
                has_gold = properties.get("has_gold", False)
                is_alive = properties.get("alive", True)
                shoot_arrow = properties.get("shoot_arrow", False)
                hear_scream = properties.get("hear_scream", False)

                self.sprite_manager.draw_agent(
                    surface,
                    int(position[0] + self.position[0]),
                    int(position[1] + self.position[1]),
                    orientation,
                    has_gold,
                    is_alive,
                    shoot_arrow,
                    hear_scream,
                )
        elif entity_data.get("name") == "Stench":
            self.sprite_manager.draw_stench(
                surface,
                int(position[0] + self.position[0]),
                int(position[1] + self.position[1]),
            )
        elif entity_data.get("name") == "Breeze":
            self.sprite_manager.draw_breeze(
                surface,
                int(position[0] + self.position[0]),
                int(position[1] + self.position[1]),
            )
        elif entity_data.get("name") == "Gold":
            self.sprite_manager.draw_gold(
                surface,
                int(position[0] + self.position[0]),
                int(position[1] + self.position[1]),
            )
