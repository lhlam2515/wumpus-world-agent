from random import choice
from .hybrid_agent import HybridAgent


class RandomAgent(HybridAgent):
    def __init__(self, size=8, k_wumpus=2, pit_prob=0.2):
        super().__init__(size, k_wumpus, pit_prob)

    def plan_route(self, current, goals, allowed):
        """Plans a route from current position to goals"""
        if isinstance(goals, (list, set)) and len(goals) == 0:
            return []

        goal = choice(list(goals)) if isinstance(goals, (list, set)) else goals

        from modules.planning import RoutePlanner
        planner = RoutePlanner(current, goal, allowed, self.size)
        return planner.plan_route()

    def plan_uncertain(self, current, risk_positions, allowed):
        """Plans a route considering uncertain positions"""
        return self.plan_route(current, risk_positions, allowed)
