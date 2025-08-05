import sys
import pygame

from modules.agent import HybridAgent
from modules.environment import WumpusWorld
from modules.visualization.map_section import MapSection
from modules.visualization.info_section import InfoSection
import modules.visualization.ui_config as config


def init_environment():
    size = 8
    agent = HybridAgent(size=size)
    wumpus_world = WumpusWorld(agent, size=size)

    env = {
        "is_running": True,
        "wumpus_world": wumpus_world,
        "agent": agent,
        "agent_name": agent.__class__.__name__,
        "is_done": False,
        "init_world": True,
        "point": 0,
        "step_count": 0,
        "has_arrow": True,
        "has_gold": False,
        "selected_world": "Random 8 x 8",
        "selected_agent": "Hybrid Agent",
    }

    return env


def initialize(env):
    main_section = MapSection(config.map_section["position"])
    info_section = InfoSection(config.info_section["position"])
    return (main_section, info_section)


def process_events(events, env):
    new_env = {**env}
    for event in events:
        if event.type == pygame.QUIT:
            new_env["is_running"] = False
            break
    return new_env


def update_state(events, dt, env, sections):
    new_env = process_events(events, env)

    if not new_env["is_running"]:
        return new_env

    # Let each section handle its events and update the environment
    for section in sections:
        new_env = section.handle_events(
            pygame.display.get_surface(), events, dt, new_env
        )

    return new_env


def render(screen, sections, env):
    # Clear the screen
    screen.fill(config.screen["bg_color"])

    map_section, info_section = sections
    map_section.render(screen)
    info_section.render(screen, env)

    # Update the display
    pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode(config.screen["size"])
    pygame.display.set_caption("Wumpus World Visualization")
    clock = pygame.time.Clock()

    env = init_environment()
    ui_sections = initialize(env)

    dt = 0
    while env["is_running"]:
        events = pygame.event.get()
        env = update_state(events, dt, env, ui_sections)
        render(screen, ui_sections, env)

        dt = clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
