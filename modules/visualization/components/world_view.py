import pygame
from .cell import Cell
import modules.visualization.ui_config as config
from modules.visualization.components.sprites import SpriteManager
from .world_data import WorldData


class WorldView(pygame.Surface):

    def __init__(self, position: tuple[int, int], world_size: int):
        """Initialize the world view with given dimensions."""
        self.board_size = config.world_view["board_size"]
        super().__init__((self.board_size, self.board_size))
        self.world_size = world_size
        self.cell_size = self.board_size / world_size
        self.sprite_manager = SpriteManager(int(self.cell_size))
        self.position = position
        self.cells = [[] for _ in range(self.world_size)]
        self._create_cells()

    def _create_cells(self):
        """Create a grid of cells for the world view."""
        for row in range(self.world_size):
            for col in range(self.world_size):
                cell = Cell(row, col, self.cell_size, self.sprite_manager)
                self.cells[row].append(cell)

    def update_world_data(self, world_data: WorldData):
        """Set the world data and update cell entities."""
        self.world_data = world_data

    def render(self):
        """Render the world view by drawing all cells."""
        priority_order = {
            "Pit": 1,
            "Wumpus": 2,
            "Agent": 3,
            "Gold": 4,
            "Stench": 5,
            "Breeze": 6,
        }

        for i in range(self.world_size):
            for j in range(self.world_size):
                cell = self.cells[i][j]
                cell.draw((0, 0), self)

                cell_pos = (
                    j,
                    self.world_size - 1 - i,
                )

                if (
                    self.world_data
                    and self.world_data.safe_cells is not None
                    and self.world_data.visited_cells is not None
                ):
                    cell.set_cell_type("unknown")
                    if cell_pos in self.world_data.safe_cells:
                        cell.set_cell_type("safe")
                    if cell_pos in self.world_data.visited_cells:
                        cell.set_cell_type("visited")

                cell.draw((0, 0), self)

                if self.world_data:
                    cell_entities = self.world_data.entities[i][j]
                    cell_entities.sort(key=lambda e: priority_order.get(e["name"], 0))
                    for entity_data in cell_entities:
                        cell.draw_entity((0, 0), self, entity_data)
