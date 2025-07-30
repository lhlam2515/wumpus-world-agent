from itertools import combinations, product
from modules.inference.knowledge import KnowledgeBase
from modules.utils import Orientation, Position, Action
from modules.inference import wumpus, pit, glitter
from modules.environment import Explorer


class HybridAgent(Explorer):
    def __init__(self, size=8, k_wumpus=2):
        self.size = size
        self.k_wumpus = k_wumpus
        self.kb = KnowledgeBase(size, k_wumpus)
        self.has_arrow = True
        self.plan = []
        self.current_position = Position()
        self.visited = set()

    @property
    def safe_points(self):
        """Get the safe points in the knowledge base."""
        for pos in product(range(self.size), repeat=2):
            if self.kb.ask_if_true([~wumpus(*pos), ~pit(*pos)]):
                yield pos

    @property
    def wumpus_positions(self):
        """Get the positions of the wumpuses."""
        for pos in product(range(self.size), repeat=2):
            if self.kb.ask_if_true([wumpus(*pos)]):
                yield pos

    @property
    def pit_positions(self):
        """Get the positions of the pits."""
        for pos in product(range(self.size), repeat=2):
            if self.kb.ask_if_true([pit(*pos)]):
                yield pos

    def execute(self, percept):
        """Execute the agent's program based on the percept."""
        x, y = self.current_position.location
        self.kb.tell_percept(x, y, percept)
        self.kb.tell(~wumpus(x, y), ~pit(x, y))

        self.visited.add((x, y))
        safe_points = set(self.safe_points)

        if self.kb.ask_if_true([glitter(x, y)]):
            goals = (0, 0)
            self.plan.append(Action.GRAB)
            actions = self.plan_route(
                self.current_position, goals, safe_points)
            self.plan.extend(actions)
            self.plan.append(Action.CLIMB)

        if len(self.plan) == 0:
            unvisited = set(
                pos for pos in product(range(self.size), repeat=2)
                if pos not in self.visited
            )

            unvisited_safe = unvisited.intersection(safe_points)

            temp = self.plan_route(
                self.current_position, unvisited_safe, safe_points
            )
            self.plan.extend(temp)

        if len(self.plan) == 0 and self.has_arrow:
            temp = self.plan_shot(
                self.current_position, self.wumpus_positions, safe_points)
            self.plan.extend(temp)

        if len(self.plan) == 0:
            uncertain_positions = set(product(range(self.size), repeat=2))
            uncertain_positions -= self.visited
            uncertain_positions -= safe_points
            uncertain_positions -= set(self.wumpus_positions)
            uncertain_positions -= set(self.pit_positions)

            temp = self.plan_route(
                self.current_position, uncertain_positions, safe_points
            )
            self.plan.extend(temp)

        if len(self.plan) == 0:
            start = (0, 0)
            temp = self.plan_route(
                self.current_position, start, safe_points
            )
            self.plan.extend(temp)
            self.plan.append(Action.CLIMB)

        action = self.plan[0]
        self.plan = self.plan[1:]
        return action

    def plan_route(self, current, goals, allowed):
        """Plan a route from the current position to the goals."""
        if isinstance(goals, list) and len(goals) == 0:
            return []

        from modules.planning import RoutePlanner
        planner = RoutePlanner(current, goals, allowed, self.size)
        return planner.plan_route()

    def plan_shot(self, current, wumpus_positions, allowed):
        """Plan a shot at the wumpus positions."""
        shoot_positions = []

        for pos in wumpus_positions:
            x, y = pos
            for p in range(0, self.size):
                if p < x and (p, y) in allowed:
                    shoot_positions.append(Position(p, y, Orientation.WEST))
                if p > x and (p, y) in allowed:
                    shoot_positions.append(Position(p, y, Orientation.EAST))
                if p < y and (x, p) in allowed:
                    shoot_positions.append(Position(x, p, Orientation.NORTH))
                if p > y and (x, p) in allowed:
                    shoot_positions.append(Position(x, p, Orientation.SOUTH))

        if len(shoot_positions) == 0:
            return []

        from modules.planning import RoutePlanner
        planner = RoutePlanner(current, shoot_positions, allowed, self.size)
        return planner.plan_route() + [Action.SHOOT]
