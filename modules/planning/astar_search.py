import heapq
from .problem import SearchProblem, Node


class PriorityFrontier():
    def __init__(self, priority_fn):
        """Initializes a priority frontier with a given priority function."""
        self.__heap = []
        self.__priority_fn = priority_fn

    def __len__(self):
        """Returns the number of nodes in the priority queue."""
        return len(self.__heap)

    def top(self) -> Node:
        """Returns the node with the highest priority without removing it."""
        if not self.__heap:
            raise IndexError("top from an empty priority queue")
        return self.__heap[0][1]

    def push(self, node) -> None:
        """Adds a node to the priority queue."""
        priority = self.__priority_fn(node)
        heapq.heappush(self.__heap, (priority, node))

    def pop(self) -> Node:
        """Removes and returns the node with the highest priority."""
        if not self.__heap:
            raise IndexError("pop from an empty priority queue")
        return heapq.heappop(self.__heap)[1]

    def is_empty(self) -> bool:
        """Checks if the priority queue is empty."""
        return len(self.__heap) == 0

    def clear(self) -> None:
        """Clears the priority queue, removing all nodes."""
        self.__heap.clear()


class AStarSearch:
    def __init__(self, problem: SearchProblem):
        """Initializes the A* search with a given problem."""
        self.problem = problem

        def priority_fn(node): return node.path_cost + \
            self.problem.heuristic(node)
        self.frontier = PriorityFrontier(priority_fn)
        self.explored = {}

    def __call__(self):
        """Executes the A* search algorithm."""
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
