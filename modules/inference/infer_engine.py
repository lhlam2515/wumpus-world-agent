from abc import ABC, abstractmethod
from itertools import combinations
from typing import Any
from .logic import Clause, Literal


class InferEngine(ABC):
    """Base class for inference engines."""

    @abstractmethod
    def __call__(self, knowledge_base, query: list[Literal]) -> Any:
        """Check if a query can be resolved with the knowledge base."""
        raise NotImplementedError("Subclasses must implement this method.")


class DPLLEngine(InferEngine):
    """DPLL-based inference engine."""

    def __call__(self, knowledge_base, query: list[Literal]) -> tuple[bool, set[Literal]]:
        """Check if a query can be resolved with the knowledge base."""
        clauses = set([*knowledge_base, Clause(*[~lit for lit in query])])
        symbols = {lit.name for clause in clauses for lit in clause}

        satisfied, model = self._dpll(clauses, symbols, set())
        return not satisfied, model

    def _dpll(self, clauses, symbols, model):
        # Remove satisfied clauses
        clauses = [c for c in clauses if not any(lit in model for lit in c)]
        # If every clause is satisfied by the model, return True
        if not clauses:
            return True, model
        # If any clause is unsatisfied (empty), return False
        if any(clause.empty() for clause in clauses):
            return False, model

        # Choose a symbol to assign
        symbol, sign = self._find_pure_symbol(symbols, clauses)
        if symbol and sign is not None:
            # print(f"Choosing pure symbol: {symbol} with sign {sign}")
            new_clauses = self._simplify(clauses, Literal(symbol, sign))
            return self._dpll(new_clauses, symbols - {symbol}, model | {Literal(symbol, sign)})

        # Choose a unit clause
        symbol, sign = self._find_unit_clause(clauses)
        if symbol and sign is not None:
            # print(f"Choosing unit clause: {symbol} with sign {sign}")
            new_clauses = self._simplify(clauses, Literal(symbol, sign))
            return self._dpll(new_clauses, symbols - {symbol}, model | {Literal(symbol, sign)})

        # If no pure symbol or unit clause, try assigning a arbitrary symbol
        symbol = next(iter(symbols))
        rest = symbols - {symbol}

        # Try assigning the symbol as True
        new_clauses = self._simplify(clauses, Literal(symbol))
        satisfied, _model = self._dpll(
            new_clauses, rest, model | {Literal(symbol)})
        if satisfied:
            return True, _model
        # Try assigning the symbol as False
        new_clauses = self._simplify(clauses, Literal(symbol, False))
        satisfied, _model = self._dpll(
            new_clauses, rest, model | {Literal(symbol, False)})
        if satisfied:
            return True, _model
        # If neither assignment leads to a solution, return False
        return False, model

    def _find_pure_symbol(self, symbols, clauses):
        """Find a pure symbol in the clauses."""
        literals = {lit for clause in clauses for lit in clause}
        for name in symbols:
            pos = any(lit.sign and lit.name == name for lit in literals)
            neg = any((not lit.sign) and lit.name == name for lit in literals)

            if pos ^ neg:  # If only one polarity exists
                return name, pos  # True if positive polarity, False if negative

        return None, None

    def _find_unit_clause(self, clauses):
        """Find a unit clause in the clauses."""
        for clause in clauses:
            if len(clause) == 1:  # If the clause has only one literal
                literal = next(iter(clause))
                return literal.name, literal.sign

        return None, None

    def _simplify(self, clauses, lit: Literal):
        """Simplify the clauses by applying the assignment of a literal."""
        new_clauses = []
        for clause in clauses:
            if lit in clause:  # If the literal is in the clause, it is satisfied
                continue
            new_clauses.append(Clause(*[l for l in clause if l != ~lit]))
        return new_clauses
