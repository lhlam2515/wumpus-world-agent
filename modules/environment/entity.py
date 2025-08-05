from modules.utils import Action, Position
from collections.abc import Callable


class Thing:
    location = None

    def __repr__(self):
        return f"{getattr(self, '__name__', self.__class__.__name__)}"


class Agent(Thing):
    def __init__(self, program=None):
        self.alive = True
        self.bump = False
        self.holding = set()
        self.performance = 0

        if program is None or not isinstance(program, Callable):
            self.program = lambda percept: Action.NOOP
        else:
            self.program = program


class Explorer(Agent):
    def __init__(self, program=None):
        super().__init__(program)
        self.position = Position()  # Default position at (0, 0) facing East
        self.holding: set[Thing] = {Arrow()}
        self.killed_by = ""
        self.visited = set()
        self.in_world = True

    @property
    def has_arrow(self):
        return any(isinstance(thing, Arrow) for thing in self.holding)

    @has_arrow.setter
    def has_arrow(self, value):
        if value:
            self.holding.add(Arrow())
        else:
            self.holding = {
                thing for thing in self.holding if not isinstance(thing, Arrow)
            }

    @property
    def has_gold(self):
        return any(isinstance(thing, Gold) for thing in self.holding)

    def grab_gold(self, thing):
        """Grab gold if present at the agent's location."""
        self.holding.add(thing) if isinstance(thing, Gold) else None


class Wumpus(Agent):
    screamed = False
    pass


class Gold(Thing):
    pass


class Pit(Thing):
    pass


class Glitter(Thing):
    pass


class Breeze(Thing):
    pass


class Stench(Thing):
    pass


class Arrow(Thing):
    pass
