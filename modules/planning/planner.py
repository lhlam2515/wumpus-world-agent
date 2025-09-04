from modules.utils import Action, Position, Orientation
from .problem import SearchProblem, Node
from .astar_search import AStarSearch


class RoutePlanner(SearchProblem):
    """Planner class for planning routes on a map.

    This class defines a search problem for finding a route from an initial
    position to one or more goal positions on a grid. It considers agent
    orientation and allowed travel squares.

    Attributes:
        size (int): The size of the square grid map.
        allowed (set[Position]): A set of allowed positions (squares) for the 
            agent to be in.
    """

    def __init__(self, initial, goals, allowed, size):
        """Initializes the RoutePlanner.

        Args:
            initial (Position): The starting position and orientation of the agent.
            goals (list[Position] | set[Position]): A list or set of goal positions.
            allowed (set[Position]): A set of allowed positions on the map.
            size (int): The size of the map grid.
        """
        super().__init__(initial, goals)
        self.size = size
        self.allowed = allowed

    def actions(self, state: Position):
        """Returns the actions that can be executed from the given state.

        Possible actions are moving forward, turning left, or turning right.
        An action is invalid if it would move the agent off the grid.

        Args:
            state (Position): The current state (position and orientation) of the agent.

        Returns:
            list[Action]: A list of valid actions from the current state.
        """
        possible_actions = [Action.FORWARD,
                            Action.TURN_LEFT, Action.TURN_RIGHT]
        x, y = state.location
        orientation = state.get_orientation()

        # Prevent moving out of bounds
        if x == 0 and orientation == Orientation.WEST:
            possible_actions.remove(Action.FORWARD)
        elif x == self.size - 1 and orientation == Orientation.EAST:
            possible_actions.remove(Action.FORWARD)
        elif y == 0 and orientation == Orientation.SOUTH:
            possible_actions.remove(Action.FORWARD)
        elif y == self.size - 1 and orientation == Orientation.NORTH:
            possible_actions.remove(Action.FORWARD)

        return possible_actions

    def result(self, state: Position, action: str):
        """Returns the new state after applying the action.

        If the action is to move forward into a disallowed square, the agent
        remains in the same location but its orientation may change if the
        action was a turn.

        Args:
            state (Position): The current state of the agent.
            action (str): The action to be performed.

        Returns:
            Position: The new state after the action.
        """
        x, y = state.location
        orientation = state.get_orientation()
        proposed_location = x, y

        if action == Action.FORWARD:
            proposed_location = Orientation.forward(orientation, x, y)
        elif action == Action.TURN_LEFT:
            orientation = Orientation.turn_left(orientation)
        elif action == Action.TURN_RIGHT:
            orientation = Orientation.turn_right(orientation)

        # Check if the proposed location is goal
        if self.goal_test(Position(*proposed_location, orientation)):
            return Position(*proposed_location, orientation)

        # Check if the proposed location is allowed
        if proposed_location not in self.allowed:
            proposed_location = x, y

        return Position(*proposed_location, orientation)

    def goal_test(self, state: Position):
        """Returns True if the state is a goal state.

        A state is a goal state if its location matches one of the goal locations.
        If goals include orientation, it must match as well.

        Args:
            state (Position): The current state to check.

        Returns:
            bool: True if the state is a goal, False otherwise.
        """
        if isinstance(self.goal, (list, set)):
            if all(isinstance(goal, Position) for goal in self.goal):
                return any(state == goal for goal in self.goal)
            else:
                return any(state.location == goal for goal in self.goal)

        if isinstance(self.goal, Position):
            return state == self.goal
        return state.location == self.goal

    def heuristic(self, node: Node) -> int:
        """Heuristic function for the planner.

        Calculates the Manhattan distance from the node's state to the nearest goal.
        If goals include orientation, a different distance metric is used.

        Args:
            node (Node): The node for which to calculate the heuristic.

        Returns:
            int: The estimated cost to reach the nearest goal.
        """
        # Calculate the Manhattan distance to the nearest goal
        def manhattan_distance(pos1, pos2):
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

        if isinstance(self.goal, (list, set)):
            if all(isinstance(goal, Position) for goal in self.goal):
                return min(sum(node.state - goal) for goal in self.goal)
            else:
                return min(manhattan_distance(node.state.location, goal) for goal in self.goal)

        if isinstance(self.goal, Position):
            return sum(node.state - self.goal)
        return manhattan_distance(node.state.location, self.goal)

    def plan_route(self):
        """Plan a route from the current position to the goals.

        Uses A* search to find the optimal path.

        Returns:
            list[Action]: A list of actions representing the planned route.
                Returns an empty list if no path is found.
        """
        result = AStarSearch(self)()
        return result.solution() if result else []
