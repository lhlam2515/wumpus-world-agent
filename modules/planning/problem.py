from abc import ABC, abstractmethod


class SearchProblem(ABC):
    """Abstract base class for search problems.

    This class defines the structure of a search problem, which includes
    the initial state, goal state, actions, results, and costs. Subclasses
    must implement the abstract methods.

    Attributes:
        initial_state: The starting state of the problem.
        goal: The goal state or a condition to be met.
    """

    def __init__(self, initial_state, goal):
        """Initializes a search problem.

        Args:
            initial_state: The initial state of the search problem.
            goal: The goal state or condition.
        """
        self.initial_state = initial_state
        self.goal = goal

    @abstractmethod
    def actions(self, state):
        """Yielding actions can be executed from the given state.

        Args:
            state: The current state.

        Raises:
            NotImplementedError: This method must be implemented by a subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def result(self, state, action):
        """Returns the state that results from executing the given action.
        The action must be one of self.actions(state).

        Args:
            state: The current state.
            action: The action to execute.

        Raises:
            NotImplementedError: This method must be implemented by a subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def goal_test(self, state):
        """Returns True if the state is a goal state.

        Args:
            state: The state to check.

        Raises:
            NotImplementedError: This method must be implemented by a subclass.
        """
        raise NotImplementedError

    def path_cost(self, cost, state1, action, state2) -> int:
        """Returns the cost of the path to the given state.

        This implementation assumes a uniform cost of 1 for each step.
        Subclasses can override this method for non-uniform costs.

        Args:
            cost (int): The cost to reach state1.
            state1: The starting state of the step.
            action: The action taken.
            state2: The resulting state.

        Returns:
            int: The total cost to reach state2.
        """
        return cost + 1

    def heuristic(self, node):
        """Heuristic function for estimating the cost to reach the goal from the state.

        A default heuristic of 0 is provided, which makes search algorithms
        like A* behave like Dijkstra's algorithm if not overridden.

        Args:
            node (Node): The node from which to estimate the cost.

        Returns:
            int: The estimated cost to the goal (0 in this case).
        """
        return 0


class Node:
    """Class representing a node in the search tree.

    A node contains a state, a reference to its parent node, the action that
    led to this state, and the total path cost from the root to this node.

    Attributes:
        state: The state represented by this node.
        parent (Node): The parent node in the search tree.
        action: The action that was taken to reach this node.
        path_cost (int): The cost of the path from the initial state to this node.
        depth (int): The depth of the node in the search tree.
    """

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Initializes a node.

        Args:
            state: The state for this node.
            parent (Node, optional): The parent node. Defaults to None.
            action (optional): The action that led to this state. Defaults to None.
            path_cost (int, optional): The cost of the path to this node. Defaults to 0.
        """
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0 if parent is None else parent.depth + 1

    def __lt__(self, node):
        """Less than comparison based on state.

        This is needed for tie-breaking in some priority queue implementations.

        Args:
            node (Node): The other node to compare with.

        Returns:
            bool: True if this node's state is less than the other's.
        """
        return self.state < node.state

    def solution(self):
        """Return the sequence of actions to reach this node from the root.

        Returns:
            list: A list of actions forming the solution path.
        """
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return the path from the root to this node.

        Returns:
            list[Node]: A list of nodes from the root to this node.
        """
        node, result = self, []
        while node:
            result.append(node)
            node = node.parent
        return list(reversed(result))

    def __eq__(self, other):
        """Check equality based on state.

        Two nodes are considered equal if they represent the same state.

        Args:
            other: The object to compare with.

        Returns:
            bool: True if the other object is a Node with the same state.
        """
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        """Hash based on state.

        The hash of a node is based on the hash of its state, allowing nodes
        to be used in sets and dictionaries.

        Returns:
            int: The hash of the node's state.
        """
        return hash(self.state)
