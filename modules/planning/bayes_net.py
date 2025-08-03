import math

# =====================
# Core Classes
# =====================


class BayesNode:
    def __init__(self, variable, parents, cpt):
        self.variable = variable
        self.parents = parents
        # Normalize cpt keys to tuples
        if isinstance(cpt, (float, int)):
            cpt = {(): cpt}
        elif isinstance(cpt, dict) and all(isinstance(k, bool) for k in cpt):
            cpt = {(k,): v for k, v in cpt.items()}
        self.cpt = cpt
        self.children = []

    def p(self, value, event):
        """Return P(self.variable=value | parent assignments in event)."""
        p_true = self.cpt[event_vals(event, self.parents)]
        return p_true if value else 1 - p_true

    def __repr__(self):
        return f"BayesNode({self.variable})"


class BayesNet:
    def __init__(self, default_prob=0.5):
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
        """Return the BayesNode for a variable, creating it with default probability if it doesn't exist."""
        if var not in self.variables():
            node = BayesNode(var, [], self.default_prob)
            self.add_node(node)
        return self.var_node[var]


class Factor:
    def __init__(self, variables, cpt):
        self.variables = variables
        self.cpt = cpt

    def pointwise_product(self, other, bn):
        """Return the pointwise product of this factor with another."""
        variables = list(set(self.variables) | set(other.variables))
        cpt = {event_vals(event, variables): self.p(event) * other.p(event)
               for event in all_events(variables, bn, {})}
        return Factor(variables, cpt)

    def sum_out(self, var, bn):
        """Sum out a variable from this factor."""
        variables = [X for X in self.variables if X != var]
        cpt = {event_vals(event, variables): sum(self.p({**event, var: val}) for val in [True, False])
               for event in all_events(variables, bn, {})}
        return Factor(variables, cpt)

    def normalize(self):
        """Normalize the factor's conditional probability table (CPT)."""
        assert len(self.variables) == 1
        total = sum(self.cpt.values())
        norm_cpt = {k: v / total for k, v in self.cpt.items()}
        return {k[0]: v for k, v in norm_cpt.items()}

    def p(self, e):
        """Return the probability of the event e given the factor's variables."""
        return self.cpt[event_vals(e, self.variables)]

# =====================
# Helper Functions
# =====================


def event_vals(event, variables):
    """Return the values of variables in event as a tuple."""
    if isinstance(event, tuple) and len(event) == len(variables):
        return event
    return tuple(event[var] for var in variables)


def all_events(variables, bn, evidence):
    """Generate all possible events for the given variables, considering evidence."""
    if not variables:
        yield evidence.copy()
    else:
        X, rest = variables[0], variables[1:]
        for event in all_events(rest, bn, evidence):
            for val in [True, False]:
                yield {**event, X: val}

# =====================
# Inference Functions
# =====================


def enumeration_ask(X, evidence, bn):
    """Return P(X=True|evidence) and P(X=False|evidence) via enumeration."""
    Q = {True: 0.0, False: 0.0}

    for x_val in (False, True):
        Q[x_val] = enumerate_all(bn.variables(), {**evidence, X: x_val}, bn)

    # Normalize
    total = Q[True] + Q[False]
    if not math.isclose(total, 1.0):
        return {True: Q[True] / total, False: Q[False] / total}
    return Q


def enumerate_all(vars_list, ev, bn):
    """Enumerate all assignments of variables in vars_list given evidence ev."""
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
    """Compute P(X|evidence) by variable elimination."""
    assert X not in evidence, "Query variable must be distinct from evidence"
    factors = []

    for var in reversed(bn.variables()):
        factors.append(make_factor(var, evidence, bn))
        if var != X and var not in evidence:  # Check if var is hidden from query
            factors = sum_out(var, factors, bn)

    result = pointwise_product(factors, bn).normalize()
    return result


def make_factor(var, evidence, bn):
    node = bn.variable_node(var)
    variables = [X for X in [var] + node.parents if X not in evidence]
    cpt = {event_vals(event, variables): node.p(event[var], event)
           for event in all_events(variables, bn, evidence)}
    return Factor(variables, cpt)


def pointwise_product(factors, bn):
    from functools import reduce
    return reduce(lambda f, g: f.pointwise_product(g, bn), factors)


def sum_out(var, factors, bn):
    result, var_factors = [], []
    for f in factors:
        if var in f.variables:
            var_factors.append(f)
        else:
            result.append(f)
    result.append(pointwise_product(var_factors, bn).sum_out(var, bn))
    return result
