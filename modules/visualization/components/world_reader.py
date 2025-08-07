import os
from modules.environment.wumpus_world import WumpusWorld
from modules.environment.entity import Thing, Gold, Pit, Wumpus, SmartWumpus
from modules.agent import HybridAgent, RandomAgent


class WorldReader:
    """A class to read the Wumpus World environment.

    The map should be a square grid with the following format:
    - . represents an empty cell
    - G represents gold
    - P represents a pit
    - W represents a wumpus

    W and P should not be placed at (0, 0), the agent is always placed at (0, 0).
    The map must contain one gold, and there can be multiple pits and wumpuses.
    Example:
    ....P...
    ..P..W..
    ........
    .....W..
    ..W....P
    P.....G.
    ....P...
    .....P..
    """

    @staticmethod
    def count_file() -> int:
        """Count the number of Wumpus World files available."""
        return len([f for f in os.listdir("test_case") if f.endswith(".txt")])

    @staticmethod
    def read_world(
        world_name: str,
        agent_class: type[HybridAgent | RandomAgent],
        wumpus_class: type[Wumpus | SmartWumpus],
    ) -> tuple[HybridAgent | RandomAgent, WumpusWorld]:
        """Read the Wumpus World from a file and return the environment."""
        file_name = "test_case/" + world_name + ".txt"
        with open(file_name, "r") as file:
            lines = file.readlines()

        size = len(lines)
        lines = [line.strip() for line in lines]

        if size == 0 or any(len(line) != size for line in lines):
            raise ValueError("The map must be a square grid.")

        world_things: list[tuple[Thing, tuple[int, int]]] = []
        pit_count = 0
        wumpus_count = 0
        gold_count = 0

        for y, line in enumerate(lines):
            for x, cell in enumerate(line):
                location = (x, size - y - 1)
                if cell == ".":
                    continue

                if cell == "G":
                    world_things.append((Gold(), location))
                    gold_count += 1
                    continue

                if cell == "P":
                    if location == (0, 0):
                        raise ValueError("Pit cannot be placed at (0, 0).")
                    world_things.append((Pit(), location))
                    pit_count += 1
                    continue

                if cell == "W":
                    if location == (0, 0):
                        raise ValueError("Wumpus cannot be placed at (0, 0).")
                    world_things.append((wumpus_class(), location))
                    wumpus_count += 1
                    continue

        if gold_count != 1:
            raise ValueError("The map must contain exactly one gold.")

        agent = agent_class(size=size, k_wumpus=wumpus_count, pit_prob=pit_count / size)
        world_things.append((agent, (0, 0)))

        return agent, WumpusWorld(None, size=size, things=world_things)
