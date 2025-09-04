import heapq
from .problem import SearchProblem, Node


class PriorityFrontier():
    """A priority queue for nodes in a search algorithm.

    This class implements a priority queue using Python's `heapq` module.
    It stores nodes and orders them based on a provided priority function.

    Attributes:
        __heap (list): A list representing the min-heap, storing tuples of
            (priority, node).
        __priority_fn (callable): A function that takes a node and returns its
            priority.
    """

    def __init__(self, priority_fn):
        """Initializes a priority frontier with a given priority function.

        Args:
            priority_fn (callable): A function that takes a node and returns its
                priority.
        """
        self.__heap = []
        self.__priority_fn = priority_fn

    def __len__(self):
        """Returns the number of nodes in the priority queue."""
        return len(self.__heap)

    def top(self) -> Node:
        """Returns the node with the highest priority without removing it.

        Returns:
            Node: The node with the highest priority (lowest priority value).

        Raises:
            IndexError: If the priority queue is empty.
        """
        if not self.__heap:
            raise IndexError("top from an empty priority queue")
        return self.__heap[0][1]

    def push(self, node) -> None:
        """Adds a node to the priority queue.

        Args:
            node (Node): The node to be added to the queue.
        """
        priority = self.__priority_fn(node)
        heapq.heappush(self.__heap, (priority, node))

    def pop(self) -> Node:
        """Removes and returns the node with the highest priority.

        Returns:
            Node: The node with the highest priority (lowest priority value).

        Raises:
            IndexError: If the priority queue is empty.
        """
        if not self.__heap:
            raise IndexError("pop from an empty priority queue")
        return heapq.heappop(self.__heap)[1]

    def is_empty(self) -> bool:
        """Checks if the priority queue is empty.

        Returns:
            bool: True if the priority queue is empty, False otherwise.
        """
        return len(self.__heap) == 0

    def clear(self) -> None:
        """Clears the priority queue, removing all nodes."""
        self.__heap.clear()


class AStarSearch:
    """Implements the A* search algorithm.

    This class provides a generic implementation of the A* search algorithm for a
    given search problem. It uses a priority queue to explore nodes with the
    lowest f-score (g-score + h-score).

    Attributes:
        problem (SearchProblem): The search problem to be solved.
        frontier (PriorityFrontier): The priority queue for managing nodes to be
            explored.
        explored (dict): A dictionary to keep track of explored states and their
            path costs.
    """

    def __init__(self, problem: SearchProblem):
        """Initializes the A* search with a given problem.

        Args:
            problem (SearchProblem): The search problem instance, which must
                conform to the SearchProblem interface (e.g., have `initial_state`,
                `goal_test`, `actions`, `result`, `path_cost`, and `heuristic`
                methods).
        """
        self.problem = problem

        def priority_fn(node):
            return node.path_cost + self.problem.heuristic(node)
        self.frontier = PriorityFrontier(priority_fn)
        self.explored = {}

    def __call__(self):
        """Executes the A* search algorithm to find a path to the goal.

        The algorithm starts from the initial state and explores nodes based on
        the A* cost function (path cost + heuristic). It keeps track of explored
        states to avoid cycles and redundant computations.

        Returns:
            Node: The goal node if a path is found, containing the solution path
                and total cost.
            None: If no solution is found (the frontier becomes empty).
        """
        initial_node = Node(self.problem.initial_state)
        self.frontier.push(initial_node)
        self.explored[initial_node.state] = 0

        while not self.frontier.is_empty():
            node = self.frontier.pop()
            if self.problem.goal_test(node.state):
                return node

            if node.path_cost > self.explored.get(
                node.state, float("inf")
            ):
                continue

            for action in self.problem.actions(node.state):
                next_state = self.problem.result(node.state, action)
                next_cost = self.problem.path_cost(
                    node.path_cost, node.state, action, next_state
                )

                if (
                    next_state not in self.explored
                    or next_cost < self.explored.get(next_state, float("inf"))
                ):
                    next_node = Node(next_state, node, action, next_cost)
                    self.frontier.push(next_node)
                    self.explored[next_state] = next_cost

        return None
