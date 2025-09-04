from abc import ABC, abstractmethod
from random import randint

from modules.utils import Action
from .entity import Agent, Thing


class Environment(ABC):
    """Abstract base class for an environment.

    An environment provides percepts to agents and executes their actions.
    It also keeps track of the state of the world.

    Attributes:
        things (list[Thing]): A list of all things in the environment.
        agents (list[Agent]): A list of all agents in the environment.
        width (int): The width of the environment grid.
        height (int): The height of the environment grid.
        time (int): The current time step.
    """

    def __init__(self, width, height):
        """Initializes an Environment.

        Args:
            width (int): The width of the environment.
            height (int): The height of the environment.
        """
        self.things = []
        self.agents = []
        self.width, self.height = width, height
        # Define the bounds of the environment
        self._x_start, self._y_start = 0, 0
        self._x_end, self._y_end = width - 1, height - 1

        self.time = 0  # Initialize time for time-based actions

    @abstractmethod
    def percept(self, agent):
        """Get the percept for the given agent.

        Args:
            agent (Agent): The agent for which to get the percept.

        Raises:
            NotImplementedError: This method must be implemented by a subclass.
        """
        raise NotImplementedError("Percept logic not implemented.")

    @abstractmethod
    def execute_action(self, agent, action):
        """Execute the given action for the specified agent.

        Args:
            agent (Agent): The agent performing the action.
            action (Action): The action to be executed.

        Raises:
            NotImplementedError: This method must be implemented by a subclass.
        """
        raise NotImplementedError("Action execution logic not implemented.")

    @abstractmethod
    def is_done(self):
        """Check if the environment is in a terminal state.

        Raises:
            NotImplementedError: This method must be implemented by a subclass.
        """
        raise NotImplementedError("Terminal state check not implemented.")

    def run(self, max_steps=None):
        """Run the environment until it reaches a terminal state or max_steps.

        Args:
            max_steps (int, optional): The maximum number of steps to run.
                If None, runs until a terminal state is reached.
        """
        if max_steps is None:
            while not self.is_done():
                self.step()
            return

        while not self.is_done() and max_steps > 0:
            max_steps -= 1
            self.step()

    def step(self):
        """Perform a single time step in the environment.

        In each step, every agent gets a percept and chooses an action.
        All actions are then executed.
        """
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
        """Check if the given coordinates are within the environment's bounds.

        Args:
            location (tuple[int, int]): The (x, y) coordinates.

        Returns:
            bool: True if the location is in bounds, False otherwise.
        """
        x, y = location
        return self._x_start <= x <= self._x_end and self._y_start <= y <= self._y_end

    def random_location(self, exclude=None):
        """Generate a random location within the environment's bounds.

        Args:
            exclude (list[tuple[int, int]], optional): A list of locations to exclude.

        Returns:
            tuple[int, int]: A random (x, y) location.
        """
        while True:
            x = randint(self._x_start, self._x_end)
            y = randint(self._y_start, self._y_end)
            if exclude is None or (x, y) not in exclude:
                return x, y

    def add_thing(self, thing, location, replace=False):
        """Add a thing to the environment at the specified location.

        Args:
            thing (Thing): The thing to add.
            location (tuple[int, int]): The location to add the thing at.
            replace (bool, optional): If True, replaces any existing thing at the location.
                Defaults to False.

        Returns:
            bool: True if the thing was added successfully, False otherwise.
        """
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
        """Remove a thing from the environment.

        Args:
            thing (Thing): The thing to remove.

        Returns:
            bool: True if the thing was removed successfully, False otherwise.
        """
        if thing not in self.things:
            return False  # Ensure the thing is in the environment

        self.things.remove(thing)
        if isinstance(thing, Agent):
            self.agents.remove(thing)
        return True

    def things_near(self, location):
        """Get all things in adjacent (non-diagonal) squares to the location.

        Args:
            location (tuple[int, int]): The center location.

        Returns:
            list[Thing]: A list of things in the neighboring squares.
        """
        x, y = location
        near_location = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

        return [thing for thing in self.things if thing.location in near_location]

    def move_to(self, thing, destination, obstacle_types=None):
        """Move a thing to the specified destination.

        The `bump` attribute of the thing is set to True if the move is
        obstructed by the environment bounds or an obstacle.

        Args:
            thing (Thing): The thing to move.
            destination (tuple[int, int]): The target location.
            obstacle_types (list[type], optional): A list of Thing types that
                are considered obstacles.

        Returns:
            bool: The value of `thing.bump`.
        """
        thing.bump = not self.is_inbounds(destination)
        if obstacle_types and self._some_things_at(destination, obstacle_types):
            thing.bump = True

        if not thing.bump:
            thing.location = destination
            if hasattr(thing, 'position'):
                thing.position.location = destination
        return thing.bump

    def _list_things_at(self, location, thing_type=Thing):
        """List all things of a given type at the specified location.

        Args:
            location (tuple[int, int]): The location to check.
            thing_type (type, optional): The type of thing to look for.
                Defaults to Thing.

        Returns:
            list[Thing]: A list of things of the specified type at the location.
        """
        return [thing for thing in self.things
                if thing.location == location and isinstance(thing, thing_type)]

    def _some_things_at(self, location, thing_type=Thing):
        """Check if there is at least one thing of a given type at a location.

        Args:
            location (tuple[int, int]): The location to check.
            thing_type (type, optional): The type of thing to look for.
                Defaults to Thing.

        Returns:
            bool: True if at least one thing of the type is found, False otherwise.
        """
        return any(self._list_things_at(location, thing_type))
