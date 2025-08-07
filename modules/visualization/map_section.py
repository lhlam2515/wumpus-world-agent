import pygame
from modules.environment import WumpusWorld
from modules.agent import HybridAgent, RandomAgent
from modules.environment.entity import Wumpus, SmartWumpus
import modules.visualization.ui_config as config
from modules.visualization.components.world_view import WorldView
from modules.visualization.components.world_data import WorldData
from modules.visualization.components.button import Button
from modules.visualization.components.selector import Selector
from modules.visualization.components.knowledge_extractor import KnowledgeExtractor
from modules.visualization.components.world_reader import WorldReader


MAX_WORLD_NUM = 3
INTERVAL_BETWEEN_STEPS = 500  # ms


class MapSection:
    """A class to represent the main map section of the game."""

    def __init__(self, position: tuple[int, int]):
        """Initialize the main map section."""
        self.world_view = None
        self.agent_view = None
        self.position = position
        self.world_position = (position[0], position[1] + 50)
        self.agent_position = (
            position[0]
            + config.world_view["board_size"]
            + config.map_section["board_spacing"],
            position[1] + 50,
        )
        self.buttons = self.__init_buttons()
        self.text = self.__init_text()
        self.selectors = self.__init_selectors()

        self.__drawn_final_world = False
        self.__have_new_step = False
        self.__needs_next_step = False

        self.__previous_step_time = 0
        self.__auto_mode = False

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

        for selector in self.selectors:
            selector.render()
            surface.blit(selector, selector.position)

    def handle_events(
        self, surface: pygame.Surface, event: pygame.event.Event, dt, env
    ):

        new_env = {**env}
        if new_env.get("needs_init_world"):
            new_env = self.__init_world_view(new_env)

        new_env = self.__process_input_events(surface, event, new_env)
        new_env = self.__update_next_step_button_state(new_env)
        self.__update_auto_step_button_state()

        self.__check_next_step_due(dt)
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

        if not self.world_view or env.get("needs_init_world", False):
            self.world_view = WorldView(self.world_position, wumpus_world.width)
            world_data = WorldData(wumpus_world.width)
            world_data.get_true_world_data(wumpus_world)
            self.world_view.update_world_data(world_data)

        if not self.agent_view or env.get("needs_init_world", False):
            self.agent_view = WorldView(self.agent_position, wumpus_world.width)
            agent_data = WorldData(wumpus_world.width)
            agent_data.get_agent_world_data(agent)
            self.agent_view.update_world_data(agent_data)

        new_env = {**env}
        agent = new_env["agent"]
        info = KnowledgeExtractor(agent).get_agent_info()
        new_env.update(info)
        new_env["needs_init_world"] = False
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
        text_style = ["text_medium", "font_medium"]

        button_configs = [
            {
                "position": (
                    self.world_position[0] + config.world_view["board_size"] // 2 + 53,
                    self.world_position[1] + config.world_view["board_size"] + 85,
                ),
                "label": "Create world",
                "variant": "primary",
                "action": self.__create_world,
            },
            {
                "position": (
                    self.agent_position[0] + config.world_view["board_size"] / 2 + 10,
                    self.world_position[1] + config.world_view["board_size"] + 50,
                ),
                "label": "Next step",
                "variant": "secondary",
                "action": self.__next_step,
            },
            {
                "position": (
                    self.agent_position[0]
                    + config.world_view["board_size"] / 2
                    - config.map_section["button_size"][0]
                    - 10,
                    self.world_position[1] + config.world_view["board_size"] + 50,
                ),
                "label": "Auto step",
                "variant": "primary",
                "action": self.__toggle_auto_mode,
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
        if env.get("is_done") or self.__auto_mode:
            next_step_button.disabled = True
        else:
            next_step_button.disabled = False

        return env

    def __update_auto_step_button_state(self):
        auto_step_button = self.buttons[2]
        if self.__auto_mode:
            auto_step_button.label = "Stop Auto"
            auto_step_button.variant = "tertiary"
        else:
            auto_step_button.label = "Auto Step"
            auto_step_button.variant = "primary"

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

            # Check for selector events
            for selector in self.selectors:
                new_env = selector.handle_event(surface, event, new_env)

        return new_env

    def __init_text(self):
        """Initialize text for the map section."""
        text = []
        text_font = pygame.font.Font(
            f"./assets/fonts/{config.map_section['text_font']}.ttf",
            config.map_section["text_size"],
        )

        thinking_text = text_font.render("Thinking...", True, config.colors["red"])
        thinking_rect = thinking_text.get_rect()

        thinking_rect.centerx = (
            self.agent_position[0] + config.world_view["board_size"] // 2
        )
        thinking_rect.top = (
            self.agent_position[1] + config.world_view["board_size"] + 10
        )
        text.append((thinking_text, thinking_rect))

        # Initialize world title text
        title_font = pygame.font.Font(
            f"./assets/fonts/{config.map_section['title_font']}.ttf",
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

    def __init_selectors(self):
        """Initialize selectors for world and agent selection."""
        pos_y = self.world_position[1] + config.world_view["board_size"] + 20

        world_selector = Selector(
            position=(
                self.world_position[0] + config.world_view["board_size"] // 2 + 10,
                pos_y,
            ),
            size=config.selector["size"],
            items=[
                "Random 4 x 4",
                "Random 8 x 8",
                "Random 10 x 10",
                "Random 12 x 12",
                "Random 16 x 16",
            ]
            + [f"World {i}" for i in range(1, MAX_WORLD_NUM + 1)],
            initial_index=1,
            on_change=self.__on_select_world,
        )

        agent_selector = Selector(
            position=(
                self.world_position[0]
                + config.world_view["board_size"] // 2
                - config.selector["size"][0]
                - 10,
                pos_y,
            ),
            size=config.selector["size"],
            items=["Hybrid Agent", "Random Agent"],
            initial_index=0,
            on_change=self.__on_select_agent,
        )

        wumpus_selector = Selector(
            position=(
                self.world_position[0]
                + config.world_view["board_size"] // 2
                - config.selector["size"][0]
                - 10,
                self.world_position[1] + config.world_view["board_size"] + 90,
            ),
            size=config.selector["size"],
            items=["Idle Wumpus", "Smart Wumpus"],
            initial_index=0,
            on_change=self.__on_select_wumpus,
        )

        return [world_selector, agent_selector, wumpus_selector]

    def _render_thinking_indicator(self, surface: pygame.Surface):
        thinking_text, thinking_rect = self.text[0]
        surface.blit(thinking_text, thinking_rect)
        pygame.display.flip()

    def __next_step(self, env):
        """Trigger the next step in the solution process."""
        if not env.get("is_done", False) and not self.__auto_mode:
            self.__needs_next_step = True

        return env

    def __toggle_auto_mode(self, env):
        self.__auto_mode = not self.__auto_mode
        if self.__auto_mode:
            self.__previous_step_time = 0
            self.__needs_next_step = False

        return env

    def __on_select_world(self, value, env):
        """Handle the map selection change."""
        new_env = {**env}
        new_env["selected_world"] = value
        return new_env

    def __on_select_agent(self, value, env):
        """Handle the agent selection change."""
        new_env = {**env}
        new_env["selected_agent"] = value
        return new_env

    def __on_select_wumpus(self, value, env):
        """Handle the wumpus mode selection change."""
        new_env = {**env}
        new_env["selected_wumpus"] = value
        return new_env

    def __create_agent(self, type, map_size):
        """Create an agent based on the selected type."""
        if type == "Hybrid Agent":
            agent = HybridAgent(size=map_size)
        elif type == "Random Agent":
            agent = RandomAgent(size=map_size)
        else:
            raise ValueError(f"Unknown agent type: {type}")
        return agent

    def __get_wumpus_class(self, wumpus_mode):
        """Get the Wumpus class based on the selected mode."""
        if wumpus_mode == "Idle Wumpus":
            return Wumpus
        elif wumpus_mode == "Smart Wumpus":
            return SmartWumpus
        else:
            raise ValueError(f"Unknown wumpus mode: {wumpus_mode}")

    def __get_agent_class(self, agent_type):
        if agent_type == "Hybrid Agent":
            return HybridAgent
        elif agent_type == "Random Agent":
            return RandomAgent
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

    def __create_world(self, env):
        """Create a new world based on the selected map and agent."""
        new_env = {**env}
        selected_world = new_env.get("selected_world", "Random 8 x 8")
        selected_agent = new_env.get("selected_agent", "Hybrid Agent")
        selected_wumpus = new_env.get("selected_wumpus", "Idle Wumpus")

        if selected_world.startswith("Random"):
            map_size = int(selected_world[-2:].strip())
            new_env = self.__random_world(
                new_env, map_size, selected_agent, selected_wumpus
            )

        else:
            map_num = selected_world[-2:].strip()
            new_env = self.__load_world(
                new_env, map_num, selected_agent, selected_wumpus
            )

        return new_env

    def __load_world(self, env, map_num, agent_type, wumpus_mode):
        """Load a predefined wumpus world."""
        new_env = {**env}

        agent_class = self.__get_agent_class(agent_type)
        wumpus_class = self.__get_wumpus_class(wumpus_mode)
        agent, wumpus_world = WorldReader.read_world(map_num, agent_class, wumpus_class)

        new_env.update(
            {
                "is_running": True,
                "wumpus_world": wumpus_world,
                "agent": agent,
                "agent_name": agent_type,
                "wumpus_mode": wumpus_mode,
                "is_done": False,
                "needs_init_world": True,
                "point": 0,
                "step_count": 0,
                "has_arrow": True,
                "has_gold": False,
                "kb_size": "N/A",
            }
        )

        self.__auto_mode = False
        self.__drawn_final_world = False
        self.__have_new_step = False
        self.__needs_next_step = False
        return new_env

    def __random_world(self, env, map_size, agent_type, wumpus_mode):
        """Generate a random world."""
        new_env = {**env}

        agent = self.__create_agent(agent_type, map_size)
        wumpus = self.__get_wumpus_class(wumpus_mode)
        wumpus_world = WumpusWorld(agent, size=map_size, wumpus_program=wumpus)

        new_env.update(
            {
                "is_running": True,
                "wumpus_world": wumpus_world,
                "agent": agent,
                "agent_name": agent_type,
                "wumpus_mode": wumpus_mode,
                "is_done": False,
                "needs_init_world": True,
                "point": 0,
                "step_count": 0,
                "has_arrow": True,
                "has_gold": False,
                "kb_size": "N/A",
            }
        )

        self.__auto_mode = False
        self.__drawn_final_world = False
        self.__have_new_step = False
        self.__needs_next_step = False
        return new_env

    def __check_next_step_due(self, dt):
        """Check if the next step is due based on the time elapsed."""
        if self.__auto_mode:
            self.__previous_step_time += dt
            if self.__previous_step_time >= INTERVAL_BETWEEN_STEPS:
                self.__previous_step_time = 0
                self.__needs_next_step = True

    def __step_world(self, surface: pygame.Surface, env):
        if env.get("is_done", False) or not self.__needs_next_step:
            return env

        new_env = {**env}

        wumpus_world = new_env.get("wumpus_world")
        if wumpus_world:
            if wumpus_world.is_done():
                new_env["is_done"] = True
                return new_env

            self._render_thinking_indicator(surface)
            wumpus_world.step()

            new_env["step_count"] += 1
            self.__needs_next_step = False
            self.__have_new_step = True

        return new_env
