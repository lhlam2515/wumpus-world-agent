# This implementation is based on the source code from the AIMA-Python project:
# https://github.com/aimacode/aima-python
from functools import reduce

# =====================
# Core Classes
# =====================


class BayesNode:
    """A node in a Bayesian network.

    Attributes:
        variable (str): The name of the variable.
        parents (list[str]): A list of parent variable names.
        cpt (dict): The conditional probability table.
        children (list[BayesNode]): A list of child nodes.
    """

    def __init__(self, variable, parents, cpt):
        """Initializes a BayesNode.

        Args:
            variable (str): The name of the variable.
            parents (list[str] or str): The parent(s) of the node.
            cpt (dict or float): The conditional probability table.
                If a float, it's the probability of the variable being True
                given no parents.
        """
        self.variable = variable
        self.parents = list(parents)  # Keep consistent order
        # Normalize CPT keys to tuples in correct parent order
        if isinstance(cpt, (float, int)):
            cpt = {(): float(cpt)}
        elif isinstance(cpt, dict) and all(isinstance(k, bool) for k in cpt):
            cpt = {(k,): float(v) for k, v in cpt.items()}
        self.cpt = cpt
        self.children = []

    def p(self, value, event):
        """Return P(self.variable=value | parent assignments in event).

        Args:
            value (bool): The value of the variable.
            event (dict): A dictionary of variable assignments.

        Returns:
            float: The conditional probability.
        """
        p_true = self.cpt[event_vals(event, self.parents)]
        p_true = clamp_prob(p_true)
        return p_true if value else 1 - p_true

    def __repr__(self):
        return f"BayesNode({self.variable})"


class BayesNet:
    """A Bayesian network.

    Attributes:
        var_node (dict[str, BayesNode]): A mapping from variable names to BayesNode objects.
        default_prob (float): The default probability for nodes created on the fly.
    """

    def __init__(self, default_prob=0.5):
        """Initializes a BayesNet.

        Args:
            default_prob (float, optional): The default probability for nodes
                created without a specified CPT. Defaults to 0.5.
        """
        self.var_node: dict[str, BayesNode] = {}
        self.default_prob = default_prob

    def add_node(self, node):
        """Add BayesNode node; parents must already exist."""
        self.var_node[node.variable] = node
        for parent in node.parents:
            self.variable_node(parent).children.append(node)

    def variables(self):
        """Return a list of variable names in the BayesNet."""
        return list(self.var_node.keys())

    def variable_node(self, var):
        """Return the BayesNode for a variable, creating it with default probability if needed."""
        if var not in self.var_node:
            node = BayesNode(var, [], self.default_prob)
            self.add_node(node)
        return self.var_node[var]


class Factor:
    """A factor in a Bayesian network, used for variable elimination.

    A factor is a function from a set of variables to a real number.
    It's represented by a conditional probability table (CPT).

    Attributes:
        variables (list[str]): A list of variable names in the factor.
        cpt (dict): The conditional probability table for the factor.
    """

    def __init__(self, variables, cpt):
        """Initializes a Factor.

        Args:
            variables (list[str]): A list of variable names.
            cpt (dict): The conditional probability table.
        """
        self.variables = list(variables)  # Keep order consistent
        self.cpt = {k: clamp_prob(v) for k, v in cpt.items()}

    def pointwise_product(self, other, bn):
        """Return the pointwise product of this factor with another.

        Args:
            other (Factor): The other factor to multiply with.
            bn (BayesNet): The Bayesian network, used for context.

        Returns:
            Factor: The resulting factor from the pointwise product.
        """
        if not self.variables:
            return other
        if not other.variables:
            return self
        variables = list(dict.fromkeys(self.variables + other.variables))
        cpt = {}
        for event in all_events(variables, bn, {}):
            val = self.p(event) * other.p(event)
            cpt[event_vals(event, variables)] = clamp_prob(val)
        return Factor(variables, cpt)

    def sum_out(self, var, bn):
        """Sum out a variable from this factor.

        Args:
            var (str): The variable to sum out.
            bn (BayesNet): The Bayesian network.

        Returns:
            Factor: A new factor with the variable summed out.
        """
        if var not in self.variables:
            return self
        variables = [X for X in self.variables if X != var]
        cpt = {}
        for event in all_events(variables, bn, {}):
            total = sum(self.p({**event, var: val}) for val in [True, False])
            cpt[event_vals(event, variables)] = clamp_prob(total)
        return Factor(variables, cpt)

    def normalize(self):
        """Normalize the factor's CPT.

        This is typically done for a factor with a single variable to get a
        probability distribution.

        Returns:
            dict: A normalized probability distribution.

        Raises:
            AssertionError: If the factor has more than one variable.
            ValueError: If the total probability is not positive.
        """
        assert len(
            self.variables) == 1, "Normalization only works on single-variable factors"
        freq = {k: v for (k,), v in self.cpt.items()}
        total = sum(freq.values())
        if total <= 0:
            raise ValueError(
                f"Invalid total probability during normalization: {total}")
        freq = {k: clamp_prob(v / total) for k, v in freq.items()}
        return freq

    def p(self, e):
        """Return the probability of the event e given this factor.

        Args:
            e (dict): An event (a dictionary of variable assignments).

        Returns:
            float: The probability of the event.
        """
        return clamp_prob(self.cpt[event_vals(e, self.variables)])


# =====================
# Helper Functions
# =====================

def clamp_prob(p):
    """Clamp probability to [0, 1] to avoid floating-point drift.

    Args:
        p (float): The probability value.

    Returns:
        float: The clamped probability.
    """
    if p < 0 and p > -1e-12:
        p = 0.0
    elif p > 1 and p < 1 + 1e-12:
        p = 1.0
    return p


def event_vals(event, variables):
    """Return the values of variables in event as a tuple.

    Args:
        event (dict or tuple): An event, which can be a dictionary of
            variable assignments or a tuple of values.
        variables (list[str]): The list of variable names.

    Returns:
        tuple: A tuple of values corresponding to the variables.
    """
    if isinstance(event, tuple) and len(event) == len(variables):
        return event
    return tuple(event[var] for var in variables)


def all_events(variables, bn, evidence):
    """Generate all possible events for the given variables, considering evidence.

    This is a recursive generator that yields all possible assignments for a
    list of variables.

    Args:
        variables (list[str]): The list of variables to generate events for.
        bn (BayesNet): The Bayesian network.
        evidence (dict): A dictionary of known variable assignments.

    Yields:
        dict: A complete assignment for the variables.
    """
    if not variables:
        yield evidence.copy()
    else:
        X, rest = variables[0], variables[1:]
        for event in all_events(rest, bn, evidence):
            if X in evidence:
                yield {**event, X: evidence[X]}
            else:
                for val in [True, False]:
                    yield {**event, X: val}


# =====================
# Inference Functions
# =====================

def enumeration_ask(X, evidence, bn):
    """Return P(X=True|evidence) and P(X=False|evidence) via enumeration.

    Args:
        X (str): The query variable.
        evidence (dict): A dictionary of observed variable assignments.
        bn (BayesNet): The Bayesian network.

    Returns:
        dict: A dictionary with the probability of X being True and False.

    Raises:
        ValueError: If the total probability is not positive.
    """
    Q = {True: 0.0, False: 0.0}
    for x_val in (False, True):
        Q[x_val] = enumerate_all(bn.variables(), {**evidence, X: x_val}, bn)
    # Normalize
    total = Q[True] + Q[False]
    if total <= 0:
        raise ValueError("Invalid probability total in enumeration.")
    return {k: clamp_prob(v / total) for k, v in Q.items()}


def enumerate_all(vars_list, ev, bn):
    """Enumerate all assignments of variables in vars_list given evidence ev.

    This is a recursive helper function for `enumeration_ask`.

    Args:
        vars_list (list[str]): The list of variables to enumerate.
        ev (dict): The evidence (known variable assignments).
        bn (BayesNet): The Bayesian network.

    Returns:
        float: The probability of the evidence.
    """
    if not vars_list:
        return 1.0
    first, rest = vars_list[0], vars_list[1:]
    node = bn.var_node[first]
    if first in ev:
        return node.p(ev[first], ev) * enumerate_all(rest, ev, bn)
    total = sum(
        node.p(val, ev) * enumerate_all(rest, {**ev, first: val}, bn)
        for val in (False, True)
    )
    return total


def elimination_ask(X, evidence, bn):
    """Compute P(X|evidence) by variable elimination.

    Args:
        X (str): The query variable.
        evidence (dict): A dictionary of observed variable assignments.
        bn (BayesNet): The Bayesian network.

    Returns:
        dict: A probability distribution for the query variable X.

    Raises:
        AssertionError: If the query variable is in the evidence.
    """
    assert X not in evidence, "Query variable must be distinct from evidence"
    factors = []
    for var in reversed(bn.variables()):
        factors.append(make_factor(var, evidence, bn))
        if var != X and var not in evidence:
            factors = sum_out(var, factors, bn)
    result = pointwise_product(factors, bn).normalize()
    return result


def make_factor(var, evidence, bn):
    """Create a factor for a variable.

    The factor's variables are the variable itself and its parents, excluding
    any variables that are part of the evidence.

    Args:
        var (str): The variable for which to create the factor.
        evidence (dict): The observed evidence.
        bn (BayesNet): The Bayesian network.

    Returns:
        Factor: The newly created factor.
    """
    node = bn.variable_node(var)
    variables = [X for X in [var] + node.parents if X not in evidence]
    cpt = {}
    for event in all_events(variables, bn, evidence):
        full_event = {**event, **evidence}  # Merge evidence for parent lookups
        cpt[event_vals(event, variables)] = node.p(full_event[var], full_event)
    return Factor(variables, cpt)


def pointwise_product(factors, bn):
    """Calculate the pointwise product of a list of factors.

    Args:
        factors (list[Factor]): A list of factors to multiply.
        bn (BayesNet): The Bayesian network.

    Returns:
        Factor: The resulting factor.
    """
    if not factors:
        return Factor([], {(): 1.0})
    return reduce(lambda f, g: f.pointwise_product(g, bn), factors)


def sum_out(var, factors, bn):
    """Sum out a variable from a list of factors.

    This function finds all factors containing the variable, computes their
    pointwise product, and then sums out the variable from the resulting factor.

    Args:
        var (str): The variable to sum out.
        factors (list[Factor]): The list of factors.
        bn (BayesNet): The Bayesian network.

    Returns:
        list[Factor]: The new list of factors after summing out the variable.
    """
    var_factors = [f for f in factors if var in f.variables]
    others = [f for f in factors if var not in f.variables]
    if not var_factors:
        return factors
    combined = pointwise_product(var_factors, bn).sum_out(var, bn)
    return others + [combined]
