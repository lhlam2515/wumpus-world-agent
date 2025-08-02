from itertools import product
from modules.inference.knowledge import KnowledgeBase
from modules.inference.logic import Clause
from modules.utils import Orientation, Position, Action
from modules.inference import wumpus, pit, glitter
from modules.environment import Explorer


class HybridAgent(Explorer):
    def __init__(self, size=8, k_wumpus=2, pit_prob=0.2, **kwargs):
        super().__init__(self.execute)
        self.size = size
        self.k_wumpus = k_wumpus
        self.pit_prob = pit_prob
        self.kb = KnowledgeBase(size, k_wumpus, **kwargs)
        self.plan = []
        self.visited = set()
        self.frontier = set()
        self.safe_points = set()

    def get_safe_positions(self):
        """Get the safe positions in the knowledge base."""
        for pos in self.frontier - self.safe_points:
            if self.kb.ask_if_true([~wumpus(*pos), ~pit(*pos)]):
                yield pos

    def get_wumpus_positions(self):
        """Get the positions of the wumpuses."""
        for pos in self.frontier - self.safe_points:
            if self.kb.ask_if_true([wumpus(*pos)]):
                yield pos

    def get_pit_positions(self):
        """Get the positions of the pits."""
        for pos in self.frontier - self.safe_points:
            if self.kb.ask_if_true([pit(*pos)]):
                yield pos

    def _neighbors(self, i, j):
        """Get the neighboring cells of (i, j)."""
        for x, y in [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]:
            if 0 <= x < self.size and 0 <= y < self.size:
                yield x, y

    def execute(self, percept):
        """Execute the agent's program based on the percept."""
        x, y = self.position.location
        self.kb.tell_percept(x, y, percept)
        self.kb.tell(~wumpus(x, y), ~pit(x, y))

        self.k_wumpus -= 1 if percept.get("scream", False) else 0

        self.visited.add((x, y))
        self.frontier.update(self._neighbors(x, y))
        self.frontier.difference_update(self.visited)

        self.safe_points.add((x, y))
        self.safe_points.update(self.get_safe_positions())

        if not self.has_gold and self.kb.ask_if_true([glitter()]):
            goals = (0, 0)
            self.plan.append(Action.GRAB) if not self.has_gold else None
            actions = self.plan_route(self.position, goals, self.safe_points)
            self.plan.extend(actions)
            self.plan.append(Action.CLIMB)

        if len(self.plan) == 0:
            unvisited_safe = self.frontier.intersection(self.safe_points)

            temp = self.plan_route(
                self.position, unvisited_safe, self.safe_points)
            self.plan.extend(temp)

        if len(self.plan) == 0:
            uncertain_positions = self.frontier - self.safe_points
            uncertain_positions -= set(self.get_wumpus_positions())
            uncertain_positions -= set(self.get_pit_positions())

            temp = self.plan_uncertain(
                self.position, uncertain_positions, self.safe_points
            )
            self.plan.extend(temp)

        if len(self.plan) == 0 and self.has_arrow:
            wumpus_positions = set(self.get_wumpus_positions())

            temp = self.plan_shot(
                self.position, wumpus_positions, self.safe_points
            )
            self.plan.extend(temp)

        if len(self.plan) == 0:
            start = (0, 0)
            temp = self.plan_route(self.position, start, self.safe_points)
            self.plan.extend(temp)
            self.plan.append(Action.CLIMB)

        action = self.plan[0]
        self.plan = self.plan[1:]
        return action

    def plan_route(self, current, goals, allowed):
        """Plan a route from the current position to the goals."""
        if isinstance(goals, (list, set)) and len(goals) == 0:
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

        return self.plan_route(current, shoot_positions, allowed) + [Action.SHOOT]

    def plan_uncertain(self, current, risk_positions, allowed):
        """Plan a route to uncertain positions."""
        if len(risk_positions) == 0:
            return []

        # Compute the probabilities of pits in uncertain positions
        pit_probabilities = self._compute_pit_probability(risk_positions)
        wumpus_probabilities = self._compute_wumpus_probability(risk_positions)
        low_risk_positions = self._filter_low_risk_positions(
            risk_positions, pit_probabilities, wumpus_probabilities
        )

        return self.plan_route(current, low_risk_positions, allowed)

    def _compute_entity_probability(self, uncertain_positions, entity_func, use_probabilistic=True, max_count=None):
        """
        Generic method to compute probability of entities (pits or wumpuses) in uncertain positions.

        Args:
            uncertain_positions: Set of positions to evaluate
            entity_func: Function (pit or wumpus) to create logical clauses
            use_probabilistic: If True, use probabilistic weighting; if False, use uniform weighting
            max_count: Maximum number of entities allowed (e.g., k_wumpus for wumpuses)
        """
        cells = [pos for pos in uncertain_positions
                 if not self.kb.ask_if_true([~entity_func(*pos)])]

        if not cells:
            return {}

        n = len(cells)
        total_weight = 0.0
        entity_weight = {cell: 0.0 for cell in cells}

        for config in product([False, True], repeat=n):
            # Skip configurations that exceed maximum count constraint
            if max_count is not None and sum(config) > max_count:
                continue

            # Create query for this configuration
            query = [Clause(entity_func(*cell)) if val else Clause(~entity_func(*cell))
                     for cell, val in zip(cells, config)]

            if self.kb.ask_if_inconsistent(query):
                continue

            # Calculate weight for this configuration
            if use_probabilistic:
                weight = 1.0
                for val in config:
                    weight *= self.pit_prob if val else (1 - self.pit_prob)
            else:
                weight = 1.0

            total_weight += weight
            for i, val in enumerate(config):
                entity_weight[cells[i]] += weight if val else 0.0

        if total_weight == 0.0:
            return {cell: 0.0 for cell in cells}

        return {cell: entity_weight[cell] / total_weight for cell in cells}

    def _compute_pit_probability(self, uncertain_positions):
        """Compute the probability of pits in uncertain positions."""
        return self._compute_entity_probability(
            uncertain_positions, pit, use_probabilistic=True
        )

    def _compute_wumpus_probability(self, uncertain_positions):
        """Compute the probability of wumpuses in uncertain positions."""
        return self._compute_entity_probability(
            uncertain_positions, wumpus, use_probabilistic=False, max_count=self.k_wumpus
        )

    def _filter_low_risk_positions(self, risk_positions, pit_prob, wumpus_prob):
        """Filter positions and return all positions with the lowest combined risk."""
        if not risk_positions:
            return []

        # Calculate combined risk for each position
        position_risks = {}
        for pos in risk_positions:
            combined_risk = pit_prob.get(pos, 0.0) + wumpus_prob.get(pos, 0.0)
            position_risks[pos] = combined_risk

        # Find the minimum risk value
        min_risk = min(position_risks.values())

        # If the minimum risk is too high, return empty list
        if min_risk > 0.5:
            return []

        # Return all positions that have the minimum risk
        lowest_risk_positions = [
            pos for pos, risk in position_risks.items() if risk == min_risk]

        return lowest_risk_positions
