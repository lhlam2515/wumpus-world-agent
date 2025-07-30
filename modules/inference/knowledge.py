from itertools import combinations
from .logic import *


class KnowledgeBase:
    """Knowledge Base for Wumpus World."""

    def __init__(self, size=8, k=2):
        self.size = size
        self.n_wumpus = k

        # Initialize the knowledge base with clauses
        self.clauses: set[Clause] = set(~(wumpus(0, 0) | pit(0, 0)))
        self.__symbols = set()  # To keep track of symbols

    def __iter__(self):
        """Iterate over the clauses in the knowledge base."""
        return iter(self.clauses)

    def __len__(self):
        """Get the number of clauses in the knowledge base."""
        return len(self.clauses)

    def __contains__(self, clause: Clause):
        """Check if a clause is in the knowledge base."""
        return clause in self.clauses

    def __repr__(self):
        """String representation of the knowledge base."""
        return "\n".join(repr(clause) for clause in sorted(self.clauses, key=lambda c: repr(c)))

    def tell(self, *clauses):
        """Add new clauses to the knowledge base."""
        if not all(isinstance(clause, (Literal, Clause)) for clause in clauses):
            raise ValueError(
                "Unexpected clause type. Must be Literal or Clause.")

        clauses = sorted(clauses, key=lambda c: repr(c))
        for clause in clauses:
            new = Clause(clause) if isinstance(clause, Literal) else clause
            # Remove negated clauses if they already exist,
            # to avoid contradictions due to the dynamic information
            if all(c in self.clauses for c in ~new):
                self.clauses.difference_update(set(~new))

            self.clauses = self.clauses.union({new})
            self.__symbols.update([lit.name for lit in new.literals])

        self.refresh()

    def tell_percept(self, i, j, percepts: dict[str, bool]):
        """Tell the knowledge base about a percept at (i, j)."""
        # 1) Create the clauses based on the percepts
        clauses = self._make_percept_clauses(i, j, percepts)

        # 2) Add the clauses to the knowledge base
        self.tell(*clauses)

    def ask_if_true(self, query: list[Literal]):
        """Check if a query can be resolved with the knowledge base."""
        if all(lit in self.clauses for lit in query):
            return True

        if any(lit.name not in self.__symbols for lit in query):
            return None

        from .infer_engine import DPLLEngine
        return DPLLEngine()(self, query)

    def refresh(self):
        """Refresh the knowledge base by removing redundant clauses."""
        # Get unit clauses as a set of unit literals
        unit_literals = {c.unit() for c in self.clauses if c.is_unit()}
        if not unit_literals:
            return

        # Remove clauses that contain unit literals
        clauses_to_remove = set()
        for clause in self.clauses:
            if not clause.is_unit() and any(lit in clause for lit in unit_literals):
                clauses_to_remove.add(clause)
        self.clauses -= clauses_to_remove

        # Simplify the clauses by removing the unit literals
        new_clauses = set()
        for clause in self.clauses:
            simplified = clause.simplify(unit_literals)
            if simplified.empty():
                raise ValueError("Knowledge base is inconsistent.")
            new_clauses.add(simplified)

        # If the new clauses are the same as the old ones, do nothing
        if new_clauses.issubset(self.clauses):
            return

        # Otherwise, update the knowledge base with the new clauses
        self.clauses = new_clauses
        self.refresh()

    def _adjacent(self, i, j):
        """Generate adjacent cells for a given cell (i, j)."""
        for di, dj in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.size and 0 <= nj < self.size:
                yield (ni, nj)

    def _make_percept_clauses(self, i, j, percepts: dict[str, bool]):
        """Generate clauses based on percepts for a given cell (i, j)."""
        clauses = set()

        for percept, value in percepts.items():
            if percept == 'breeze':
                clauses.add(breeze(i, j) if value else ~breeze(i, j))
                clauses.update(self._breeze_axioms(i, j))
            elif percept == 'stench':
                clauses.add(stench(i, j) if value else ~stench(i, j))
                clauses.update(self._stench_axioms(i, j))
            elif percept == 'glitter':
                clauses.add(glitter(i, j) if value else ~glitter(i, j))

        # No Wumpus and Pit in the same cell
        clauses.add(~wumpus(i, j) | ~pit(i, j))

        return clauses

    def _breeze_axioms(self, i, j):
        """Generate Breeze axioms for a given cell (i, j)."""
        B = breeze(i, j)
        P_adj = [pit(*p) for p in self._adjacent(i, j)]

        # If Breeze is true, then at least one adjacent Pit must be true
        yield ~B | Clause(*P_adj)

        # If any adjacent Pit is true, then Breeze must be true
        yield from (~P | B for P in P_adj)

    def _stench_axioms(self, i, j):
        """Generate Stench axioms for a given cell (i, j)."""
        S = stench(i, j)
        W_adj = [wumpus(*w) for w in self._adjacent(i, j)]

        # If Stench is true, then at least one adjacent Wumpus must be true
        yield ~S | Clause(*W_adj)

        # If any adjacent Wumpus is true, then Stench must be true
        yield from (~W | S for W in W_adj)
