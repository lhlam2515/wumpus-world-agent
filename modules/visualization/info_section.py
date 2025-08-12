import pygame
import modules.visualization.ui_config as config
from modules.visualization.components.panel import Panel


class InfoSection:

    def __init__(self, position: tuple[int, int]):
        self.position = position
        self.info_panel = self.__init_info_panel()
        self.game_indicators = self.__init_game_indicators()

    def render(self, surface: pygame.Surface, env):
        self.__update_info_panel(env)
        self.__update_game_indicators(env)

        surface.blit(self.info_panel, self.info_panel.position)
        surface.blit(self.game_indicators, self.game_indicators.position)

    def handle_events(self, surface: pygame.Surface, events, dt: float, env):
        new_env = {**env}

        return new_env

    def __init_info_panel(self) -> Panel:
        items = {
            "Agent": "N/A",
            "Wumpus": "N/A",
            "Step": "0",
            "Points": "0",
            "KB size": "N/A",
            "Has arrow": "N/A",
            "Has gold": "N/A",
            "Agent status": "N/A",
        }

        item_size = config.panel["item_height"] + config.panel["item_spacing"]

        return Panel(
            position=(self.position[0], self.position[1]),
            size=(
                config.panel["width"],
                56 + item_size * len(items),
            ),
            title="Game Infos",
            items=items,
        )

    def __init_game_indicators(self) -> Panel:
        """Initialize the game indicators panel."""
        items = {
            "Agent": "Blue circle",
            "Gold": "Yellow diamond",
            "Wumpus": "Brown circle",
            "Pit": "Dark gray square",
            "Breeze": "Blue wavy line",
            "Stench": "Red wavy line",
            "Safe": "Green cell",
            "Safe visited": "White cell",
            "Unknown": "Gray cell",
        }

        item_size = config.panel["item_height"] + config.panel["item_spacing"]

        return Panel(
            position=(
                self.position[0],
                self.position[1] + self.info_panel.size[1] + 20,
            ),
            size=(
                config.panel["width"],
                56 + item_size * len(items),
            ),
            title="Game Indicators",
            items=items,
        )

    def __update_info_panel(self, env: dict) -> None:
        """Update the info panel with the current game state."""
        status = "N/A"
        is_alive = env.get("alive", True)
        if is_alive:
            if not env.get("in_world", True):
                status = "Climbed out"
            else:
                status = "Alive"
        else:
            killed_by = env.get("killed_by", "unknown")
            if killed_by.endswith("Wumpus"):
                killed_by = "Wumpus"
            status = "Killed by " + killed_by

        self.info_panel.render(
            {
                "Agent": env.get("agent_name", "N/A"),
                "Wumpus": env.get("wumpus_mode", "N/A"),
                "Step": env.get("step_count", 0),
                "Points": env.get("performance", 0),
                "KB size": env.get("kb_size", "N/A"),
                "Has arrow": env.get("has_arrow", "True"),
                "Has gold": env.get("has_gold", "False"),
                "Agent status": status,
            }
        )

    def __update_game_indicators(self, env: dict) -> None:
        self.game_indicators.render()
