from itertools import product
from random import random as get_probability
from modules.utils import Action
from .environment import Environment
from .entity import Explorer, Gold, Pit, Wumpus


class WumpusWorld(Environment):
    """A Wumpus World environment for the Wumpus World agent."""

    def __init__(self, agent_program, size=8, k_wumpus=2, pit_probability=0.2):
        super().__init__(size, size)
        self.init_world(agent_program, k_wumpus, pit_probability)

    def init_world(self, agent_program, k_wumpus, pit_probability):
        """Spawn agents, wumpuses, and pits in the environment."""

        # TODO: Implement the logic to spawn wumpuses and pits in the environment.

        # TODO: Implement the logic to spawn gold in the environment.

        # TODO: Implement the logic to spawn the agent in the environment.
        # * If agent_program is a list, spawn multiple agents. Otherwise, spawn a single agent.

    def get_world(self):
        """Return the items in the Wumpus World."""
        # TODO: Implement the logic to return the items in the Wumpus World.
        # * This should be a grid-like structure representing the Wumpus World.
        # * Each cell should contain the items present in that cell.
        raise NotImplementedError

    def percept(self, agent):
        """Get the percept for the given agent."""
        # TODO: Implement the logic to get the percept for the agent.
        raise NotImplementedError("percept() is not implemented yet.")

    def execute_action(self, agent, action):
        """Execute the given action for the specified agent."""
        # TODO: Implement the logic to execute the action for the agent.
        # * This should update the agent's state and the environment accordingly.
        raise NotImplementedError("execute_action() is not implemented yet.")

    def in_danger(self, agent):
        """Check if Explorer is in danger, if he is, kill him."""
        # TODO: Implement the logic to check if the agent is in danger.
        raise NotImplementedError("in_danger() is not implemented yet.")

    def is_done(self):
        """Check if the environment is in a terminal state."""
        # TODO: Implement the logic to check if the environment is in a terminal state.
        # * This is over when all agents are dead or climbed out of the cave.
        raise NotImplementedError("is_done() is not implemented yet.")
