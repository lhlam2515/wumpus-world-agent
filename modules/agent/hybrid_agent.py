from itertools import product
from modules.inference.knowledge import KnowledgeBase
from modules.planning.bayes_net import BayesNet, BayesNode, elimination_ask
from modules.utils import Orientation, Position, Action
from modules.inference import wumpus, pit,  breeze, stench, glitter, scream
from modules.environment import Explorer


class HybridAgent(Explorer):
    def __init__(self, size=8, k_wumpus=2, pit_prob=0.2):
        super().__init__(self.execute)
        self.size = size
        self.k_wumpus = k_wumpus
        self.pit_prob = pit_prob
        self.kb = KnowledgeBase(size)
        self.plan = []
        self.visited = set()
        self.frontier = set()

    @property
    def safe_positions(self):
        """Get the safe positions in the knowledge base."""
        positions = set()
        for pos in self.visited | self.frontier:
            if self.kb.ask_if_true([~wumpus(*pos), ~pit(*pos)]):
                positions.add(pos)
        return positions

    @property
    def wumpus_positions(self):
        """Get the positions of the wumpuses."""
        positions = set()
        for pos in self.frontier - self.safe_positions:
            if self.kb.ask_if_true([wumpus(*pos)]):
                positions.add(pos)
        return positions

    @property
    def pit_positions(self):
        """Get the positions of the pits."""
        positions = set()
        for pos in self.frontier - self.safe_positions:
            if self.kb.ask_if_true([pit(*pos)]):
                positions.add(pos)
        return positions

    @property
    def breeze_positions(self):
        """Get the positions of the breezes."""
        positions = set()
        for pos in self.visited:
            if self.kb.ask_if_true([breeze(*pos)]):
                positions.add(pos)
        return positions

    @property
    def stench_positions(self):
        """Get the positions of the stenches."""
        positions = set()
        for pos in self.visited:
            if self.kb.ask_if_true([stench(*pos)]):
                positions.add(pos)
        return positions

    def _neighbors(self, i, j):
        """Get the neighboring cells of (i, j)."""
        for x, y in [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]:
            if 0 <= x < self.size and 0 <= y < self.size:
                yield x, y

    def execute(self, percept, time):
        """Execute the agent's program based on the percept."""
        x, y = self.position.location
        self.kb.tell_percept(x, y, percept)
        self.kb.tell(~wumpus(x, y), ~pit(x, y))

        self.k_wumpus -= 1 if percept.get("scream", False) else 0

        self.visited.add((x, y))
        self.frontier.update(self._neighbors(x, y))
        self.frontier.difference_update(self.visited)

        safe_positions = self.safe_positions

        self.plan = []  # Reset plan due to dynamic environment
        if (time + 1) % 5 == 0:
            safe_positions -= set(pos for pos in self.stench_positions)

        if self.kb.ask_if_true([glitter()]):
            goals = (0, 0)
            self.plan.append(Action.GRAB) if not self.has_gold else None
            temp = self.plan_route(self.position, goals, safe_positions)
            self.plan.extend(temp)
            self.plan.append(Action.CLIMB)

        if len(self.plan) == 0:
            unvisited_safe = self.frontier.intersection(safe_positions)

            temp = self.plan_route(
                self.position, unvisited_safe, safe_positions
            )
            self.plan.extend(temp)

        if len(self.plan) == 0:
            uncertain_positions = set(self.frontier) - set(safe_positions)
            uncertain_positions -= self.pit_positions
            uncertain_positions -= self.wumpus_positions

            temp = self.plan_uncertain(
                self.position, uncertain_positions, safe_positions
            )
            self.plan.extend(temp)

        if len(self.plan) == 0 and self.has_arrow:
            temp = self.plan_shot(
                self.position, self.wumpus_positions, safe_positions,
                sub_positions=self.stench_positions
            )
            self.plan.extend(temp)

        if len(self.plan) == 0 and self.kb.ask_if_true([scream()]):
            temp = self.plan_route(
                self.position, self.stench_positions, safe_positions
            )
            self.plan.extend(temp)

        if len(self.plan) == 0:
            start = (0, 0)
            temp = self.plan_route(self.position, start, safe_positions)
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

    def plan_shot(self, current, wumpus_positions, allowed, sub_positions=None):
        """Plan a shot at the wumpus positions."""
        shoot_positions = []

        for pos in wumpus_positions:
            x, y = pos
            for p in range(0, self.size):
                if p < x and (p, y) in allowed:
                    shoot_positions.append(Position(p, y, Orientation.EAST))
                if p > x and (p, y) in allowed:
                    shoot_positions.append(Position(p, y, Orientation.WEST))
                if p < y and (x, p) in allowed:
                    shoot_positions.append(Position(x, p, Orientation.NORTH))
                if p > y and (x, p) in allowed:
                    shoot_positions.append(Position(x, p, Orientation.SOUTH))

        if not shoot_positions and sub_positions:
            for x, y in sub_positions:
                shoot_positions.append(Position(x, y, Orientation.EAST))
                shoot_positions.append(Position(x, y, Orientation.WEST))
                shoot_positions.append(Position(x, y, Orientation.NORTH))
                shoot_positions.append(Position(x, y, Orientation.SOUTH))

        if not shoot_positions:
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

        print(f"Pit probabilities: {pit_probabilities}")
        print(f"Wumpus probabilities: {wumpus_probabilities}")
        print(f"Low risk positions: {low_risk_positions}")

        return self.plan_route(current, low_risk_positions, allowed)

    def _compute_pit_probability(self, uncertain_positions):
        """Compute the probability of pits in uncertain positions."""
        uncertain_positions = set(pos for pos in uncertain_positions
                                  if self.kb.ask_if_true([~pit(*pos)]) is None)
        return self._compute_entity_probability(
            uncertain_positions, pit, self.pit_prob
        )

    def _compute_wumpus_probability(self, uncertain_positions):
        """Compute the probability of wumpuses in uncertain positions."""
        uncertain_positions = set(pos for pos in uncertain_positions
                                  if self.kb.ask_if_true([~wumpus(*pos)]) is None)
        return self._compute_entity_probability(
            uncertain_positions, wumpus, self.k_wumpus / self.size**2
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
        import math
        lowest_risk_positions = [
            pos for pos, risk in position_risks.items()
            if math.isclose(risk, min_risk)
        ]

        return lowest_risk_positions

    def _compute_entity_probability(self, positions, entity_func, entity_prob):
        """Compute the probability of entities in uncertain positions."""
        entity_pos = self.pit_positions if entity_func.__name__ == "pit" else self.wumpus_positions
        percept_func = breeze if entity_func.__name__ == "pit" else stench
        percept_pos = self.breeze_positions if percept_func.__name__ == "breeze" else self.stench_positions

        cells = positions | entity_pos
        if not cells:
            return {}

        # Create BayesNet for entities
        bayes_net = BayesNet()
        for cell in cells:
            node = BayesNode(entity_func(*cell).name, [], entity_prob)
            bayes_net.add_node(node)

        evidence = {}

        # Add percept nodes to the BayesNet
        known_percepts = map(
            lambda pos: percept_func(*pos).name, percept_pos
        )
        for node in self._make_bayes_node(known_percepts, cells, entity_func):
            bayes_net.add_node(node)
            evidence[node.variable] = True

        # Add known entities to the BayesNet
        known_entities = map(
            lambda pos: entity_func(*pos).name, entity_pos
        )
        for node in self._make_bayes_node(known_entities, percept_pos, percept_func, any=False):
            bayes_net.add_node(node)
            evidence[node.variable] = True

        results = {}
        for cell in cells - entity_pos:
            var = entity_func(*cell).name
            post = elimination_ask(var, evidence, bayes_net)
            results[cell] = post[True]
        return results

    def _make_bayes_node(self, variables, frontier, entity_func, **kwargs):
        nodes = []
        func = any if kwargs.get("any", True) else all

        for var in variables:
            parents = []
            _, x, y = var.split("_")
            for cell in self._neighbors(int(x), int(y)):
                if cell in frontier:
                    parents.append(entity_func(*cell).name)
            if not parents:
                continue  # Skip if no parents
            # Build CPT: if Percept is true, then entity is likely present
            cpt = {}
            for combo in product([True, False], repeat=len(parents)):
                cpt[combo] = func(combo)
            nodes.append(BayesNode(var, parents, cpt))

        return nodes
