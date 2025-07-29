from itertools import combinations
from .logic import *


class KnowledgeBase:
    """Knowledge Base for Wumpus World."""

    def __init__(self, size=8, k=2):
        self.size = size
        self.n_wumpus = k

        # Initialize the knowledge base with clauses
        self.clauses: set[Clause] = self._init_axioms()

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

        clauses = set(clauses)
        for clause in clauses:
            new = Clause(clause) if isinstance(clause, Literal) else clause

            if all(c in self.clauses for c in ~new):
                # Remove the old clauses that are subsumed by the new clause
                self.clauses.difference_update(set(~new))
            self.clauses = self.clauses.union({new})

    def tell_breeze(self, i, j, value: bool):
        """Tell the knowledge base about a Breeze percept."""
        # 1) Create the Breeze and Pit literals
        B = breeze(i, j)
        P_adj = [pit(*p) for p in self._make_adjacent(i, j)]

        # 2) Add the clauses to the knowledge base
        # 2a) If Breeze is true, then at least one adjacent Pit must be true
        self.tell(~B | Clause(*P_adj))

        # 2b) If any adjacent Pit is true, then Breeze must be true
        self.tell(*[~P | B for P in P_adj])

        # 3) Add the observed Breeze value
        self.tell(Clause(B) if value else Clause(~B))

    def tell_stench(self, i, j, value: bool):
        """Tell the knowledge base about a Stench percept."""
        # 1) Create the Stench and Wumpus literals
        S = stench(i, j)
        W_adj = [wumpus(*w) for w in self._make_adjacent(i, j)]

        # 2) Add the clauses to the knowledge base
        # 2a) If Stench is true, then at least one adjacent Wumpus must be true
        self.tell(~S | Clause(*W_adj))

        # 2b) If any adjacent Wumpus is true, then Stench must be true
        self.tell(*[~W | S for W in W_adj])

        # 3) Add the observed Stench value
        self.tell(Clause(S) if value else Clause(~S))

    def _init_axioms(self):
        """Initialize the axioms for the Wumpus World."""
        clauses: set[Clause] = set()

        # 1/ Start point is (0, 0) safe <=> no Wumpus or Pit
        clauses.add(Clause(~wumpus(0, 0)))
        clauses.add(Clause(~pit(0, 0)))

        # 2/ ???

        return clauses

    def _make_adjacent(self, i, j):
        """Generate adjacent cells for a given cell (i, j)."""
        for di, dj in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.size and 0 <= nj < self.size:
                yield (ni, nj)
