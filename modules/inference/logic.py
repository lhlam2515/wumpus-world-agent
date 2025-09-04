class Literal:
    """Represents a literal in propositional logic.

    A literal is an atomic formula (a propositional variable) or its negation.

    Attributes:
        name (str): The name of the propositional variable.
        sign (bool): True for a positive literal, False for a negative (negated) literal.
    """

    def __init__(self, name, sign=True):
        """Initializes a Literal.

        Args:
            name (str): The name of the literal.
            sign (bool, optional): The sign of the literal. Defaults to True.
        """
        self.name = name
        self.sign = sign  # True for positive, False for negated

    def __hash__(self):
        """Computes the hash of the literal."""
        return hash((self.name, self.sign))

    def __eq__(self, other):
        """Checks if two literals are equal."""
        return (self.name, self.sign) == (other.name, other.sign)

    def __repr__(self):
        """Returns the string representation of the literal."""
        return ("" if self.sign else "¬") + self.name

    def __invert__(self):
        """Returns the negation of the literal."""
        return Literal(self.name, not self.sign)

    def __or__(self, other):
        """Creates a clause by ORing this literal with another literal or clause.

        Args:
            other (Literal | Clause): The other literal or clause.

        Returns:
            Clause: A new clause containing the literals.

        Raises:
            TypeError: If the other operand is not a Literal or Clause.
        """
        if isinstance(other, Literal):
            return Clause(self, other)
        elif isinstance(other, Clause):
            if ~self in other:
                return Clause()
            return Clause(self, *other.literals)

        raise TypeError(f"Unsupported {type(other)} for OR operation")


class Clause():
    """Represents a clause in propositional logic.

    A clause is a disjunction of literals.

    Attributes:
        literals (set[Literal]): A set of literals in the clause.
    """

    def __init__(self, *literals):
        """Initializes a Clause.

        Args:
            *literals: A variable number of Literal objects.
        """
        self.literals = set(literals)

    def __hash__(self):
        """Computes the hash of the clause."""
        return hash(tuple(sorted(self.literals, key=lambda x: (x.sign, x.name))))

    def __eq__(self, other):
        """Checks if two clauses are equal."""
        return self.literals == other.literals

    def __repr__(self):
        """Returns the string representation of the clause."""
        return " ∨ ".join(repr(lit) for lit in sorted(self.literals, key=lambda x: (x.sign, x.name)))

    def __iter__(self):
        """Returns an iterator over the literals in the clause."""
        return iter(self.literals)

    def __len__(self):
        """Returns the number of literals in the clause."""
        return len(self.literals)

    def __contains__(self, literal):
        """Checks if a literal is in the clause.

        Args:
            literal (Literal): The literal to check for.

        Returns:
            bool: True if the literal is in the clause, False otherwise.
        """
        if isinstance(literal, Literal):
            return literal in self.literals
        return False

    def __invert__(self):
        """Returns the negation of the clause (De Morgan's laws).

        If the clause is a unit clause, it returns a negated clause.
        Otherwise, it returns a list of negated unit clauses.

        Returns:
            Clause | list[Clause]: The negated clause(s).
        """
        negated = [Clause(~lit) for lit in self.literals]
        return negated[0] if len(negated) == 1 else negated

    def __or__(self, other):
        """Creates a new clause by ORing this clause with another literal or clause.

        Args:
            other (Literal | Clause): The other literal or clause.

        Returns:
            Clause: A new clause containing the combined literals.

        Raises:
            TypeError: If the other operand is not a Literal or Clause.
        """
        if isinstance(other, Literal):
            return Clause(*self.literals, other)
        elif isinstance(other, Clause):
            if any(~lit in self for lit in other):
                return Clause()
            return Clause(*self.literals, *other.literals)

        raise TypeError(f"Unsupported {type(other)} for OR operation")

    def empty(self):
        """Checks if the clause is empty."""
        return len(self.literals) == 0

    def is_unit(self):
        """Check if the clause is a unit clause (contains only one literal)."""
        return len(self.literals) == 1

    def unit(self):
        """Get the unit literal if the clause is a unit clause.

        Returns:
            Literal: The single literal in the clause.

        Raises:
            ValueError: If the clause is not a unit clause.
        """
        if self.is_unit():
            return next(iter(self.literals))
        raise ValueError("Clause is not a unit clause")

    def simplify(self, model):
        """Simplify the clause based on the current model.

        If a literal in the clause is true in the model, the clause is satisfied (returns None).
        If a literal is false, it is removed from the clause.

        Args:
            model (set[Literal]): A set of literals known to be true.

        Returns:
            Clause | None: A new, simplified clause, or None if the clause is satisfied.
        """
        literals = []
        for lit in self.literals:
            if lit in model:
                return None  # This clause is satisfied by the model
            if ~lit in model:
                continue  # This literal is false in the model
            literals.append(lit)

        return Clause(*literals)


def wumpus(i, j):
    """Create a Wumpus literal at position (i, j).

    Args:
        i (int): The row.
        j (int): The column.

    Returns:
        Literal: A literal representing the presence of a Wumpus.
    """
    return Literal(f"W_{i}_{j}")


def pit(i, j):
    """Create a Pit literal at position (i, j).

    Args:
        i (int): The row.
        j (int): The column.

    Returns:
        Literal: A literal representing the presence of a Pit.
    """
    return Literal(f"P_{i}_{j}")


def breeze(i, j):
    """Create a Breeze literal at position (i, j).

    Args:
        i (int): The row.
        j (int): The column.

    Returns:
        Literal: A literal representing the presence of a Breeze.
    """
    return Literal(f"B_{i}_{j}")


def stench(i, j):
    """Create a Stench literal at position (i, j).

    Args:
        i (int): The row.
        j (int): The column.

    Returns:
        Literal: A literal representing the presence of a Stench.
    """
    return Literal(f"S_{i}_{j}")


def glitter():
    """Create a Glitter literal.

    Returns:
        Literal: A literal representing the presence of Glitter.
    """
    return Literal("Glitter")


def bump(i, j):
    """Create a Bump literal at position (i, j).

    Args:
        i (int): The row.
        j (int): The column.

    Returns:
        Literal: A literal representing a Bump.
    """
    return Literal(f"Bu_{i}_{j}")


def scream():
    """Create a Scream literal.

    Returns:
        Literal: A literal representing a Scream.
    """
    return Literal("Scream")
