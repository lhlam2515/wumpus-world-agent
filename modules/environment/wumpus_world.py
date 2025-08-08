import random
from typing import Iterator
from itertools import product
from modules.utils import Action
from .environment import Environment
from .entity import Explorer, Gold, Pit, Wumpus, Thing


class WumpusWorld(Environment):
    """A Wumpus World environment for the Wumpus World agent."""

    def __init__(
        self, agent_program, size=8, k_wumpus=2, pit_density=0.2, **kwargs
    ):
        super().__init__(size, size)
        self.wumpus_program = kwargs.get("wumpus_program", Wumpus)
        if things := kwargs.get("things", None):
            self.init_world_from_map(things)
        else:
            self.init_world(agent_program, k_wumpus, pit_density)

    def init_world(self, agent_program, k_wumpus, pit_density):
        """Spawn agents, wumpuses, and pits in the environment."""
        pit_locations = []
        wumpus_locations = []

        # Spawn pits in the environment
        num_pits = int(self.width * self.height * pit_density)
        while len(pit_locations) < num_pits:
            location = self.random_location(
                exclude=[(0, 0), (1, 0), (0, 1)]
            )

            if self.add_thing(Pit(), location):
                pit_locations.append(location)

        # Spawn wumpuses in the environment
        while len(wumpus_locations) < k_wumpus:
            location = self.random_location(
                exclude=[(0, 0), (1, 0), (0, 1), *pit_locations]
            )
            if self.add_thing(self.wumpus_program(), location):
                wumpus_locations.append(location)

        # Spawn gold in the environment.
        gold_location = self.random_location(
            exclude=[*pit_locations, *wumpus_locations]
        )
        self.add_thing(Gold(), gold_location)

        # Spawn the agent in the environment.
        if isinstance(agent_program, list):
            for agent in agent_program:
                self.add_thing(agent, (0, 0), replace=True)
        else:
            self.add_thing(agent_program, (0, 0), replace=True)

    def init_world_from_map(self, things: list[tuple[Thing, tuple[int, int]]]):
        """Initialize the world with a predefined list of things."""
        for thing, location in things:
            self.add_thing(thing, location, replace=True)

    def get_world(self) -> Iterator[list[list[Thing]]]:
        """Return the items in the Wumpus World."""
        world = [
            [[] for _ in range(self._x_start, self._x_end + 1)]
            for _ in range(self._y_start, self._y_end + 1)
        ]
        for thing in self.things:
            y, x = thing.location
            if self.is_inbounds((x, y)):
                world[x - self._x_start][y - self._y_start].append(thing)
        return reversed(world)

    def percept(self, agent):
        """Get the percept for the given agent."""
        things_near = self.things_near(agent.location)

        percepts: dict[str, bool] = {
            "breeze": any(isinstance(thing, Pit) for thing in things_near),
            "stench": any(
                isinstance(thing, Wumpus) and thing.alive for thing in things_near
            ),
        }

        # Check for bump (if agent bumped into a wall)
        percepts["bump"] = agent.bump if hasattr(agent, "bump") else False

        # Check for glitter (gold) only at the agent's location
        if any(self._list_things_at(agent.location, Gold)):
            percepts["glitter"] = True

        # Check for scream (wumpus death)
        wumpuses = [
            thing for thing in self.things if isinstance(thing, Wumpus)]
        for wumpus in wumpuses:
            if not wumpus.alive and not wumpus.screamed:
                percepts["scream"] = True
                wumpus.screamed = True

        if not isinstance(agent, Wumpus):
            return percepts

        # ========== WUMPUS PERCEPT ========== #
        # Check for the present of Explorer
        percepts["explorer"] = any(
            isinstance(thing, Explorer) and thing.alive
            for thing in self._list_things_at(agent.location)
        )

        return percepts

    def execute_action(self, agent, action):
        """Execute the given action for the specified agent."""
        if isinstance(agent, Explorer) and self.in_danger(agent):
            return

        agent.bump = False
        if action == Action.FORWARD:
            new_location = Action.forward(agent.position).location
            agent.bump = self.move_to(agent, new_location)
            agent.performance -= 1
        elif action == Action.TURN_LEFT:
            agent.position = Action.turn_left(agent.position)
            agent.performance -= 1
        elif action == Action.TURN_RIGHT:
            agent.position = Action.turn_right(agent.position)
            agent.performance -= 1
        elif action == Action.GRAB:  # Only triggered when gold at agent's location
            if self._some_things_at(agent.position.location, Gold):
                agent.grab_gold(Gold())
                self.things = [
                    thing for thing in self.things if not isinstance(thing, Gold)
                ]
            agent.performance += 10 if agent.has_gold else 0
        elif action == Action.CLIMB:
            if agent.location == (0, 0):
                agent.performance += 1000 if agent.has_gold else 0
                agent.in_world = False
                self.remove_thing(agent)
        elif action == Action.SHOOT:
            if agent.has_arrow:
                arrow_travel = Action.forward(agent.position)
                while self.is_inbounds(arrow_travel.location):
                    wumpus = self._list_things_at(
                        arrow_travel.location, Wumpus)
                    if wumpus:
                        wumpus[0].alive = False  # type: ignore
                        print(
                            f"Wumpus at {arrow_travel.location} has been killed!")
                        break
                    arrow_travel = Action.forward(arrow_travel)
                agent.has_arrow = False
                agent.performance -= 10

        # ========== WUMPUS ACTIONS ========== #
        elif action == Action.KILL:  # Only triggered when Explorer at Wumpus location
            list_things_at = self._list_things_at(agent.location)
            for thing in list_things_at:
                if isinstance(thing, Explorer) and thing.alive:
                    thing.alive = False
                    thing.killed_by = "Wumpus"
                    thing.performance -= 1000

        elif action == Action.MOVE:  # Move Wumpus randomly
            direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
            new_location = (
                agent.location[0] + direction[0],  # type: ignore
                agent.location[1] + direction[1],  # type: ignore
            )  # type: ignore
            agent.bump = self.move_to(agent, new_location, (Pit, Wumpus))

    def in_danger(self, agent):
        """Check if Explorer is in danger, if he is, kill him."""
        if not agent.alive:
            return True  # Agent is already dead

        things_at_location = self._list_things_at(agent.position.location)
        for thing in things_at_location:
            if isinstance(thing, Pit) or (isinstance(thing, Wumpus) and thing.alive):
                agent.alive, agent.killed_by = False, thing.__class__.__name__
                agent.performance -= 1000
                return True
        return False

    def is_done(self):
        """Check if the environment is in a terminal state."""
        explorer = [
            agent for agent in self.agents if isinstance(agent, Explorer)]
        # Check if all explorers are dead or have climbed out
        if explorer:
            if all(self.in_danger(agent) or not agent.alive for agent in explorer):
                return True
            else:
                return False
        return True  # No explorers left, environment is done
