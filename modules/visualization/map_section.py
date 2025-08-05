import pygame
from modules.visualization.components.world_view import WorldView
from modules.visualization.components.world_data import WorldData
import modules.visualization.ui_config as config
from modules.visualization.components.button import Button
from modules.visualization.components.knowledge_extractor import KnowledgeExtractor
from modules.environment import WumpusWorld
from modules.agent import HybridAgent


class MapSection:
    """A class to represent the main map section of the game."""

    def __init__(self, position: tuple[int, int]):
        """Initialize the main map section."""
        self.world_view = None
        self.agent_view = None
        self.position = position
        self.world_position = (position[0], position[1] + 70)
        self.agent_position = (
            position[0]
            + config.world_view["board_size"]
            + config.map_section["board_spacing"],
            position[1] + 70,
        )
        self.buttons = self.__init_buttons()
        self.text = self.__init_text()

        self.__drawn_final_world = False
        self.__have_new_step = False

    def render(self, surface: pygame.Surface):
        """Render the main map section."""
        if self.world_view and self.agent_view:
            self.world_view.render()
            surface.blit(self.world_view, self.world_position)
            self.agent_view.render()
            surface.blit(self.agent_view, self.agent_position)

        for button in self.buttons:
            button.draw(surface)

        for text, rect in self.text[1:]:
            surface.blit(text, rect)

    def handle_events(
        self, surface: pygame.Surface, event: pygame.event.Event, dt, env
    ):

        new_env = {**env}
        if new_env.get("init_world"):
            new_env = self.__init_world_view(new_env)

        new_env = self.__process_input_events(surface, event, new_env)
        new_env = self.__update_next_step_button_state(new_env)
        new_env = self.__step_world(surface, new_env)

        if self.__have_new_step:
            new_env = self.__update_world_data(new_env)

        if new_env.get("is_done", False) and not self.__drawn_final_world:
            new_env = self.__update_world_data(new_env)
            self.__drawn_final_world = True

        return new_env

    def __init_world_view(self, env):
        """Initialize the world view."""
        wumpus_world = env.get("wumpus_world")
        agent = env.get("agent")

        if not wumpus_world or not agent:
            return

        if not self.world_view or env.get("init_world", False):
            self.world_view = WorldView(self.world_position, wumpus_world.width)
            world_data = WorldData(wumpus_world.width)
            world_data.get_true_world_data(wumpus_world)
            self.world_view.update_world_data(world_data)

        if not self.agent_view or env.get("init_world", False):
            self.agent_view = WorldView(self.agent_position, wumpus_world.width)
            agent_data = WorldData(wumpus_world.width)
            agent_data.get_agent_world_data(agent)
            self.agent_view.update_world_data(agent_data)

        new_env = {**env}
        agent = new_env["agent"]
        info = KnowledgeExtractor(agent).get_agent_info()
        new_env.update(info)
        new_env["init_world"] = False
        return new_env

    def __update_world_data(self, env):
        """Update the world data for both views."""
        new_env = {**env}
        wumpus_world = new_env.get("wumpus_world")
        agent = new_env.get("agent")

        if not wumpus_world or not agent:
            return new_env

        if not self.world_view or not self.agent_view:
            self.__init_world_view(new_env)
            return new_env

        world_data = self.world_view.world_data
        world_data.get_true_world_data(wumpus_world)
        self.world_view.update_world_data(world_data)

        agent_data = self.agent_view.world_data
        agent_data.get_agent_world_data(agent)
        self.agent_view.update_world_data(agent_data)

        self.__have_new_step = False

        info = KnowledgeExtractor(agent).get_agent_info()
        new_env.update(info)

        return new_env

    def __init_buttons(self):
        """Initialize buttons for the main map section."""
        size = config.map_section["button_size"]
        text_style = ["text_small", "font_family"]
        pos_y = self.world_position[1] + config.world_view["board_size"] + 40

        button_configs = [
            {
                "position": (
                    self.position[0]
                    + config.world_view["board_size"] / 2
                    - config.map_section["button_size"][0] / 2,
                    pos_y,
                ),
                "label": "Random map",
                "variant": "secondary",
                "action": self.__random_map,
            },
            {
                "position": (
                    self.position[0]
                    + config.world_view["board_size"]
                    + config.map_section["board_spacing"]
                    + config.world_view["board_size"] / 2
                    - config.map_section["button_size"][0] / 2,
                    pos_y,
                ),
                "label": "Next step",
                "variant": "primary",
                "action": self.__next_step,
            },
        ]

        return [
            Button(
                config["position"],
                size,
                config["label"],
                config["variant"],
                text_style,
                action=config["action"],
            )
            for config in button_configs
        ]

    def __update_next_step_button_state(self, env):
        next_step_button = self.buttons[1]
        if env.get("is_done"):
            next_step_button.disabled = True
        else:
            next_step_button.disabled = False

        return env

    def __process_input_events(self, surface: pygame.Surface, events, env):
        new_env = {**env}

        for event in events:
            # Check for keyboard events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    new_env = self.__next_step(new_env)
                    break
                elif event.key == pygame.K_ESCAPE:
                    new_env["is_running"] = False
                    break

            # Check for button clicks
            for button in self.buttons:
                if not button.disabled and button.is_clicked(surface, event):
                    # Call the button's action function with the environment
                    if button.action:
                        new_env = button.action(new_env)
                    break

        return new_env

    def __init_text(self):
        """Initialize text for the map section."""
        text = []
        text_font = pygame.font.Font(
            f"./assets/fonts/{config.map_section['font_family']}.ttf",
            config.map_section["text_size"],
        )

        thinking_text = text_font.render("Thinking...", True, config.colors["red"])
        thinking_rect = thinking_text.get_rect()

        button_pos = self.buttons[1].position
        thinking_rect.centerx = button_pos[0] + self.buttons[1].size[0] // 2
        thinking_rect.bottom = button_pos[1] - 10
        text.append((thinking_text, thinking_rect))

        # Initialize world title text
        title_font = pygame.font.Font(
            f"./assets/fonts/{config.map_section['font_family']}.ttf",
            config.map_section["title_size"],
        )
        world_title = title_font.render(
            "World Map", True, config.map_section["title_color"]
        )
        world_title_rect = world_title.get_rect()
        world_title_rect.centerx = (
            self.world_position[0] + config.world_view["board_size"] // 2
        )
        world_title_rect.bottom = self.world_position[1] - 10
        text.append((world_title, world_title_rect))

        # Initialize agent title text
        agent_title = title_font.render(
            "Agent Knowledge", True, config.map_section["title_color"]
        )
        agent_title_rect = agent_title.get_rect()
        agent_title_rect.centerx = (
            self.agent_position[0] + config.world_view["board_size"] // 2
        )
        agent_title_rect.bottom = self.agent_position[1] - 10
        text.append((agent_title, agent_title_rect))
        return text

    def _render_thinking_indicator(self, surface: pygame.Surface):
        thinking_text, thinking_rect = self.text[0]
        surface.blit(thinking_text, thinking_rect)
        pygame.display.flip()

    def __next_step(self, env):
        """Trigger the next step in the solution process."""
        new_env = {**env}
        if new_env.get("is_done", False):
            return new_env
        new_env["next_step"] = True
        return new_env

    def __random_map(self, env):
        """Generate a random map."""
        new_env = {**env}
        size = 8
        agent = HybridAgent(size=size)
        wumpus_world = WumpusWorld(agent, size=size)

        new_env.update(
            {
                "is_running": True,
                "wumpus_world": wumpus_world,
                "agent": agent,
                "is_done": False,
                "init_world": True,
                "point": 0,
                "step_count": 0,
                "has_arrow": True,
                "has_gold": False,
                "kb_size": "N/A",
                "next_step": False,
            }
        )

        self.__drawn_final_world = False
        self.__have_new_step = False
        return new_env

    def __step_world(self, surface: pygame.Surface, env):
        new_env = {**env}
        if new_env.get("is_done", False) or not new_env.get("next_step", False):
            return new_env

        wumpus_world = new_env.get("wumpus_world")
        if wumpus_world:
            if wumpus_world.is_done():
                new_env["is_done"] = True
                return new_env

            self._render_thinking_indicator(surface)
            wumpus_world.step()

            new_env["step_count"] += 1
            new_env["next_step"] = False
            self.__have_new_step = True

        return new_env
