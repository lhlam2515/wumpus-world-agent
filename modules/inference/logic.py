class Literal:
    def __init__(self, name, sign=True):
        self.name = name
        self.sign = sign  # True for positive, False for negated

    def __hash__(self):
        return hash((self.name, self.sign))

    def __eq__(self, other):
        return (self.name, self.sign) == (other.name, other.sign)

    def __repr__(self):
        return ("" if self.sign else "¬") + self.name

    def __invert__(self):
        return Literal(self.name, not self.sign)

    def __or__(self, other):
        if isinstance(other, Literal):
            return Clause(self, other)
        elif isinstance(other, Clause):
            if ~self in other:
                return Clause()
            return Clause(self, *other.literals)

        raise TypeError(f"Unsupported {type(other)} for OR operation")


class Clause():
    def __init__(self, *literals):
        self.literals = set(literals)

    def __hash__(self):
        return hash(tuple(sorted(self.literals, key=lambda x: (x.sign, x.name))))

    def __eq__(self, other):
        return self.literals == other.literals

    def __repr__(self):
        return " ∨ ".join(repr(lit) for lit in sorted(self.literals, key=lambda x: (x.sign, x.name)))

    def __iter__(self):
        return iter(self.literals)

    def __len__(self):
        return len(self.literals)

    def __contains__(self, literal):
        if isinstance(literal, Literal):
            return literal in self.literals
        return False

    def __invert__(self):
        negated = [Clause(~lit) for lit in self.literals]
        return negated[0] if len(negated) == 1 else negated

    def __or__(self, other):
        if isinstance(other, Literal):
            return Clause(*self.literals, other)
        elif isinstance(other, Clause):
            if any(~lit in self for lit in other):
                return Clause()
            return Clause(*self.literals, *other.literals)

        raise TypeError(f"Unsupported {type(other)} for OR operation")

    def empty(self):
        return len(self.literals) == 0

    def is_unit(self):
        """Check if the clause is a unit clause (contains only one literal)."""
        return len(self.literals) == 1

    def unit(self):
        """Get the unit literal if the clause is a unit clause."""
        if self.is_unit():
            return next(iter(self.literals))
        raise ValueError("Clause is not a unit clause")

    def simplify(self, model):
        """Simplify the clause based on the current model."""
        literals = []
        for lit in self.literals:
            if lit in model:
                return None  # This clause is satisfied by the model
            if ~lit in model:
                continue  # This literal is false in the model
            literals.append(lit)

        return Clause(*literals)


def wumpus(i, j):
    """Create a Wumpus literal."""
    return Literal(f"W_{i}_{j}")


def pit(i, j):
    """Create a Pit literal."""
    return Literal(f"P_{i}_{j}")


def breeze(i, j):
    """Create a Breeze literal."""
    return Literal(f"B_{i}_{j}")


def stench(i, j):
    """Create a Stench literal."""
    return Literal(f"S_{i}_{j}")


def glitter():
    """Create a Glitter literal."""
    return Literal("Glitter")


def bump(i, j):
    """Create a Bump literal."""
    return Literal(f"Bu_{i}_{j}")


def scream():
    """Create a Scream literal."""
    return Literal(f"Scream")
