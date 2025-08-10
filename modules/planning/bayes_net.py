from functools import reduce

# =====================
# Core Classes
# =====================


class BayesNode:
    def __init__(self, variable, parents, cpt):
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
        """Return P(self.variable=value | parent assignments in event)."""
        p_true = self.cpt[event_vals(event, self.parents)]
        p_true = clamp_prob(p_true)
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
        """Return the BayesNode for a variable, creating it with default probability if needed."""
        if var not in self.var_node:
            node = BayesNode(var, [], self.default_prob)
            self.add_node(node)
        return self.var_node[var]


class Factor:
    def __init__(self, variables, cpt):
        self.variables = list(variables)  # Keep order consistent
        self.cpt = {k: clamp_prob(v) for k, v in cpt.items()}

    def pointwise_product(self, other, bn):
        """Return the pointwise product of this factor with another."""
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
        """Sum out a variable from this factor."""
        if var not in self.variables:
            return self
        variables = [X for X in self.variables if X != var]
        cpt = {}
        for event in all_events(variables, bn, {}):
            total = sum(self.p({**event, var: val}) for val in [True, False])
            cpt[event_vals(event, variables)] = clamp_prob(total)
        return Factor(variables, cpt)

    def normalize(self):
        """Normalize the factor's CPT."""
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
        """Return the probability of the event e given this factor."""
        return clamp_prob(self.cpt[event_vals(e, self.variables)])


# =====================
# Helper Functions
# =====================

def clamp_prob(p):
    """Clamp probability to [0, 1] to avoid floating-point drift."""
    if p < 0 and p > -1e-12:
        p = 0.0
    elif p > 1 and p < 1 + 1e-12:
        p = 1.0
    return p


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
            if X in evidence:
                yield {**event, X: evidence[X]}
            else:
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
    if total <= 0:
        raise ValueError("Invalid probability total in enumeration.")
    return {k: clamp_prob(v / total) for k, v in Q.items()}


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
        if var != X and var not in evidence:
            factors = sum_out(var, factors, bn)
    result = pointwise_product(factors, bn).normalize()
    return result


def make_factor(var, evidence, bn):
    node = bn.variable_node(var)
    variables = [X for X in [var] + node.parents if X not in evidence]
    cpt = {}
    for event in all_events(variables, bn, evidence):
        full_event = {**event, **evidence}  # Merge evidence for parent lookups
        cpt[event_vals(event, variables)] = node.p(full_event[var], full_event)
    return Factor(variables, cpt)


def pointwise_product(factors, bn):
    if not factors:
        return Factor([], {(): 1.0})
    return reduce(lambda f, g: f.pointwise_product(g, bn), factors)


def sum_out(var, factors, bn):
    var_factors = [f for f in factors if var in f.variables]
    others = [f for f in factors if var not in f.variables]
    if not var_factors:
        return factors
    combined = pointwise_product(var_factors, bn).sum_out(var, bn)
    return others + [combined]
