from abc import ABC, abstractmethod
from random import randint

from modules.utils import Action
from .entity import Agent, Thing


class Environment(ABC):
    def __init__(self, width, height):
        self.things = []
        self.agents = []
        self.width, self.height = width, height
        # Define the bounds of the environment
        self._x_start, self._y_start = 0, 0
        self._x_end, self._y_end = width - 1, height - 1

        self.time = 0  # Initialize time for time-based actions

    @abstractmethod
    def percept(self, agent):
        """Get the percept for the given agent."""
        raise NotImplementedError("Percept logic not implemented.")

    @abstractmethod
    def execute_action(self, agent, action):
        """Execute the given action for the specified agent."""
        raise NotImplementedError("Action execution logic not implemented.")

    @abstractmethod
    def is_done(self):
        """Check if the environment is in a terminal state."""
        raise NotImplementedError("Terminal state check not implemented.")

    def run(self, max_steps=None):
        """Run the environment until it reaches a terminal state."""
        if max_steps is None:
            while not self.is_done():
                self.step()
            return

        while not self.is_done() and max_steps > 0:
            max_steps -= 1
            self.step()

    def step(self):
        """Perform a single step in the environment."""
        actions = []
        for agent in self.agents:
            if agent.alive:
                actions.append(agent.program(self.percept(agent), self.time))
            else:
                actions.append(Action.NOOP)

        agents = [*self.agents]
        for agent, action in zip(agents, actions):
            if action is not Action.NOOP:
                self.execute_action(agent, action)

        self.time += 1  # Increment time after all actions are executed

    def is_inbounds(self, location):
        """Check if the given coordinates are within the environment's bounds."""
        x, y = location
        return self._x_start <= x <= self._x_end and self._y_start <= y <= self._y_end

    def random_location(self, exclude=None):
        """Generate a random location within the environment's bounds."""
        while True:
            x = randint(self._x_start, self._x_end)
            y = randint(self._y_start, self._y_end)
            if exclude is None or (x, y) not in exclude:
                return x, y

    def add_thing(self, thing, location, replace=False):
        """Add a thing to the environment at the specified location."""
        if not self.is_inbounds(location):
            return False
        thing.location = location

        if not replace and self._some_things_at(location):
            return False

        self.things.append(thing)
        if isinstance(thing, Agent):
            self.agents.append(thing)
        return True

    def remove_thing(self, thing):
        """Remove a thing from the environment."""
        if thing not in self.things:
            return False  # Ensure the thing is in the environment

        self.things.remove(thing)
        if isinstance(thing, Agent):
            self.agents.remove(thing)
        return True

    def things_near(self, location):
        """Get all things near the specified location."""
        x, y = location
        near_location = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

        return [thing for thing in self.things if thing.location in near_location]

    def move_to(self, thing, destination, obstacle_types=None):
        """Move a thing to the specified destination."""
        thing.bump = not self.is_inbounds(destination)
        if obstacle_types and self._some_things_at(destination, obstacle_types):
            thing.bump = True

        if not thing.bump:
            thing.location = destination
            if hasattr(thing, 'position'):
                thing.position.location = destination
        return thing.bump

    def _list_things_at(self, location, thing_type=Thing):
        """List all things at the specified coordinates."""
        return [thing for thing in self.things
                if thing.location == location and isinstance(thing, thing_type)]

    def _some_things_at(self, location, thing_type=Thing):
        """Check if there is at least one thing of the specified type at the given coordinates."""
        return any(self._list_things_at(location, thing_type))
