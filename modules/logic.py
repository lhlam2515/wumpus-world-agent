"""Logic utilities for propositional reasoning in Wumpus World.

This module provides core logical reasoning capabilities including
expression representation, CNF conversion, knowledge base management,
and inference algorithms for the Wumpus World domain.
"""

from typing import List, Dict, Optional, Union, Tuple
import re


class Expr:
    """Represents a propositional logic expression.

    This class provides a tree-based representation for propositional
    logic expressions including atomic propositions, negation, and
    complex logical operators.

    Attributes:
        op: The operator or symbol name.
        args: Arguments to the operator (empty for atomic propositions).
    """

    def __init__(self, op: str, *args):
        """Initialize a logical expression.

        Args:
            op: Operator symbol or proposition name.
            *args: Arguments for the operator.
        """
        self.op = op
        self.args = args

    def __repr__(self):
        """Return string representation of the expression."""
        if not self.args:
            return self.op
        return f"({self.op} {' '.join(map(str, self.args))})"

    def __eq__(self, other):
        """Check equality with another expression."""
        return isinstance(other, Expr) and self.op == other.op and self.args == other.args

    def __invert__(self):
        """Create negation of this expression using ~ operator."""
        return Expr('not', [self])


def expr(s: str) -> Expr:
    """Parse a propositional logic string into an Expr tree.

    Supports propositional logic syntax including symbols, parentheses,
    and standard logical operators.

    Args:
        s: String representation of logical expression.

    Returns:
        Expr tree representing the parsed expression.

    Raises:
        NotImplementedError: Parser not yet implemented.
    """
    # TODO: Implement recursive descent or shunting-yard parser
    # Should handle: ~, &, |, =>, <=> operators and parentheses
    raise NotImplementedError("Expression parsing not implemented yet")


def to_cnf(e: Expr) -> Expr:
    """Convert expression to Conjunctive Normal Form.

    Performs the standard CNF conversion process:
    1. Eliminate biconditionals and implications
    2. Push negations inward (De Morgan's laws)
    3. Distribute disjunction over conjunction

    Args:
        e: Expression to convert to CNF.

    Returns:
        Equivalent expression in CNF form.
    """
    # TODO: Implement full CNF conversion algorithm
    return e


def conjuncts(e: Expr) -> List[Expr]:
    """Extract conjunct clauses from a CNF expression.

    Given an expression in CNF, returns the list of clauses
    that are connected by conjunction.

    Args:
        e: CNF expression to decompose.

    Returns:
        List of clause expressions.
    """
    # TODO: Implement conjunct extraction
    return [e]


class PropDefiniteKB:
    """Knowledge base for definite Horn clauses.

    Manages a collection of definite Horn clauses and provides
    forward chaining inference for entailment checking.

    Attributes:
        clauses: List of stored clauses in CNF form.
    """

    def __init__(self):
        """Initialize an empty knowledge base."""
        self.clauses: List[Expr] = []

    def tell(self, clause: Expr) -> None:
        """Add a definite clause to the knowledge base.

        Args:
            clause: Logical clause to add (will be converted to CNF).
        """
        self.clauses.append(to_cnf(clause))

    def ask(self, query: Expr) -> bool:
        """Check if query is entailed by the knowledge base.

        Args:
            query: Query expression to check for entailment.

        Returns:
            True if query is entailed, False otherwise.
        """
        return pl_fc_entails(self.clauses, query)


def pl_fc_entails(clauses: List[Expr], query: Expr) -> bool:
    """Count-based forward chaining for Horn clause entailment.

    Implements the forward chaining algorithm to determine if
    a query is logically entailed by a set of Horn clauses.

    Args:
        clauses: List of Horn clauses in the knowledge base.
        query: Query to check for entailment.

    Returns:
        True if clauses entail query, False otherwise.
    """
    # TODO: Implement forward chaining algorithm:
    # 1. Initialize count of premises for each implication
    # 2. Maintain set of known facts
    # 3. Repeatedly apply modus ponens until fixpoint
    return False


def dpll_satisfiable(sentence: Expr) -> Union[Dict[str, bool], bool]:
    """Determine satisfiability using DPLL algorithm.

    Implements the DPLL algorithm for determining satisfiability
    of propositional logic sentences.

    Args:
        sentence: Propositional logic sentence to check.

    Returns:
        Dictionary representing satisfying model if satisfiable,
        False if unsatisfiable.
    """
    # TODO: Implement DPLL algorithm:
    # 1. Convert to CNF and extract clauses
    # 2. Unit propagation
    # 3. Pure literal elimination
    # 4. Recursive search with variable assignment
    return False


# Wumpus World domain-specific predicates

def pit(x: int, y: int) -> Expr:
    """Create pit predicate for position (x, y).

    Args:
        x: X-coordinate.
        y: Y-coordinate.

    Returns:
        Expr representing Pit(x, y).
    """
    return Expr("P", x, y)


def wumpus(x: int, y: int) -> Expr:
    """Create wumpus predicate for position (x, y).

    Args:
        x: X-coordinate.
        y: Y-coordinate.

    Returns:
        Expr representing Wumpus(x, y).
    """
    return Expr("W", x, y)


def breeze(x: int, y: int) -> Expr:
    """Create breeze predicate for position (x, y).

    Args:
        x: X-coordinate.
        y: Y-coordinate.

    Returns:
        Expr representing Breeze(x, y).
    """
    return Expr("B", x, y)


def stench(x: int, y: int) -> Expr:
    """Create stench predicate for position (x, y).

    Args:
        x: X-coordinate.
        y: Y-coordinate.

    Returns:
        Expr representing Stench(x, y).
    """
    return Expr("S", x, y)


def ok_to_move(x: int, y: int) -> Expr:
    """Create safe movement predicate for position (x, y).

    A cell is safe to move to if it contains neither pit nor wumpus.

    Args:
        x: X-coordinate.
        y: Y-coordinate.

    Returns:
        Expr representing ¬Pit(x,y) ∧ ¬Wumpus(x,y).
    """
    return Expr('and', Expr('not', pit(x, y)), Expr('not', wumpus(x, y)))
