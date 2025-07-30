from .problem import SearchProblem, Node
from modules.utils import Position, Orientation


class RoutePlanner(SearchProblem):
    """Planner class for planning routes on a map."""

    def __init__(self, initial, goals, allowed, size):
        super().__init__(initial, goals)
        self.size = size
        self.allowed = allowed

    def actions(self, state: Position):
        """Returns the actions that can be executed from the given state."""
        possible_actions = ["Forward", "TurnLeft", "TurnRight"]
        x, y = state.location
        orientation = state.get_orientation()

        # Prevent moving out of bounds
        if x == 0 and orientation == Orientation.WEST:
            possible_actions.remove("Forward")
        elif x == self.size - 1 and orientation == Orientation.EAST:
            possible_actions.remove("Forward")
        elif y == 0 and orientation == Orientation.SOUTH:
            possible_actions.remove("Forward")
        elif y == self.size - 1 and orientation == Orientation.NORTH:
            possible_actions.remove("Forward")

        return possible_actions

    def result(self, state: Position, action: str):
        """Returns the new state after applying the action."""
        x, y = state.location
        orientation = state.get_orientation()
        proposed_location = x, y

        if action == "Forward":
            proposed_location = Orientation.forward(orientation, x, y)
        elif action == "TurnLeft":
            orientation = Orientation.turn_left(orientation)
        elif action == "TurnRight":
            orientation = Orientation.turn_right(orientation)

        # Check if the proposed location is allowed
        if proposed_location not in self.allowed:
            proposed_location = x, y

        return Position(*proposed_location, orientation)

    def goal_test(self, state: Position):
        """Returns True if the state is a goal state."""
        if isinstance(self.goal, list):
            if all(isinstance(goal, Position) for goal in self.goal):
                return any(state == goal for goal in self.goal)
            else:
                return any(state.location == goal for goal in self.goal)

        if isinstance(self.goal, Position):
            return state == self.goal
        return state.location == self.goal

    def heuristic(self, node: Node) -> int:
        """Heuristic function for the planner."""
        # Calculate the Manhattan distance to the nearest goal
        def manhattan_distance(pos1, pos2):
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

        if isinstance(self.goal, list):
            if all(isinstance(goal, Position) for goal in self.goal):
                return min(node.state - goal for goal in self.goal)
            else:
                return min(manhattan_distance(node.state.location, goal) for goal in self.goal)

        if isinstance(self.goal, Position):
            return node.state - self.goal
        return manhattan_distance(node.state.location, self.goal)

    def plan_route(self):
        """Plan a route from the current position to the goals."""
        from .astar_search import AStarSearch

        result = AStarSearch(self)()
        if result is None:
            return []
        return result.solution()
