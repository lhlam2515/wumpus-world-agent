from abc import ABC, abstractmethod


class SearchProblem(ABC):
    """Abstract base class for search problems."""

    def __init__(self, initial_state, goal):
        """Initializes a search problem with an initial state.

        Args:
            initial_state: The initial state of the search problem.
            goal: The goal state or condition.
        """
        self.initial_state = initial_state
        self.goal = goal

    @abstractmethod
    def actions(self, state):
        """Yielding actions can be executed from the given state."""
        raise NotImplementedError

    @abstractmethod
    def result(self, state, action):
        """Returns the state that results from executing the given action.
        The action must be one of self.actions(state).
        """
        raise NotImplementedError

    @abstractmethod
    def goal_test(self, state):
        """Returns True if the state is a goal state."""
        raise NotImplementedError

    def path_cost(self, cost, state1, action, state2) -> int:
        """Returns the cost of the path to the given state."""
        return cost + 1

    def heuristic(self, node):
        """Heuristic function for estimating the cost to reach the goal from the state."""
        return 0


class Node:
    """Class representing a node in the search tree."""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Initializes a node with the given state, parent, action, and path cost."""
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0 if parent is None else parent.depth + 1

    def __lt__(self, node):
        """Less than comparison based on state."""
        return self.state < node.state

    def solution(self):
        """Return the sequence of actions to reach this node from the root."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return the path from the root to this node."""
        node, result = self, []
        while node:
            result.append(node)
            node = node.parent
        return list(reversed(result))

    def __eq__(self, other):
        """Check equality based on state."""
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        """Hash based on state."""
        return hash(self.state)
