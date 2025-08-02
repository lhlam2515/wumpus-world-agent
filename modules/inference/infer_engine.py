from abc import ABC, abstractmethod
from typing import Any
from .logic import Clause, Literal


class InferEngine(ABC):
    """Base class for inference engines."""

    @abstractmethod
    def __call__(self, knowledge_base, query: Clause | list[Clause]) -> Any:
        """Check if a query can be resolved with the knowledge base."""
        raise NotImplementedError("Subclasses must implement this method.")


class DPLLEngine(InferEngine):
    """DPLL satisfiable inference engine."""

    def __call__(self, knowledge_base, query: Clause | list[Clause]) -> bool:
        """Check if a query can be resolved with the knowledge base."""
        clauses = set([*knowledge_base])
        if isinstance(query, Clause):
            clauses.add(query)
        elif isinstance(query, list) and all(isinstance(q, Clause) for q in query):
            clauses.update(query)
        else:
            raise ValueError("Query must be a list of Literals or Clauses.")

        symbols = {lit.name for clause in clauses for lit in clause}

        return self._dpll(clauses, symbols, set())

    def _dpll(self, clauses, symbols, model):
        # Remove satisfied clauses
        unknown_clauses = [c for c in clauses
                           if not any(lit in model for lit in c)]
        # If every clause is satisfied by the model, return True
        if len(unknown_clauses) == 0:
            return True
        # If any clause is unsatisfied (empty), return False
        unknown_clauses = map(lambda c: c.simplify(model), unknown_clauses)
        if any(c.empty() for c in unknown_clauses):
            return False

        # Choose a symbol to assign
        symbol, sign = self._find_pure_symbol(symbols, unknown_clauses)
        if symbol and sign is not None:
            literal = Literal(symbol, sign)
            return self._dpll(
                clauses, symbols - {symbol}, model.union({literal})
            )

        # Choose a unit clause
        symbol, sign = self._find_unit_clause(clauses, model)
        if symbol and sign is not None:
            literal = Literal(symbol, sign)
            return self._dpll(
                clauses, symbols - {symbol}, model.union({literal})
            )

        # If no pure symbol or unit clause, try assigning a arbitrary symbol
        symbol = next(iter(symbols))
        rest = symbols - {symbol}

        # Try assigning the symbol as True
        if self._dpll(clauses, rest, model | {Literal(symbol, True)}):
            return True
        if self._dpll(clauses, rest, model | {Literal(symbol, False)}):
            return True
        return False

    def _find_pure_symbol(self, symbols, clauses):
        """Find a pure symbol in the clauses."""
        literals = {lit for clause in clauses for lit in clause}
        for name in symbols:
            pos = any(lit.sign and lit.name == name for lit in literals)
            neg = any((not lit.sign) and lit.name == name for lit in literals)

            if pos ^ neg:  # If only one polarity exists
                return name, pos  # True if positive polarity, False if negative

        return None, None

    def _find_unit_clause(self, clauses, model):
        """Find a unit clause in the clauses."""
        for clause in clauses:
            clause = clause.simplify(model)
            if clause and clause.is_unit():
                return clause.unit().name, clause.unit().sign

        return None, None
