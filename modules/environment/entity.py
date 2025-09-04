from modules.utils import Action, Position
from collections.abc import Callable


class Thing:
    """Base class for all objects that can appear in an Environment.

    Attributes:
        location: The location of the thing in the environment.
    """
    location = None

    def __repr__(self):
        """Return a string representation of the Thing."""
        return f"{getattr(self, '__name__', self.__class__.__name__)}"


class Agent(Thing):
    """An agent is a Thing that can act in an environment.

    The agent's behavior is determined by its program, which takes a percept
    and the current time as input and returns an action.

    Attributes:
        alive (bool): Whether the agent is alive.
        bump (bool): Whether the agent has bumped into something.
        holding (set): A set of things the agent is holding.
        performance (int): The agent's performance score.
        program (Callable): The agent's program.
    """

    def __init__(self, program=None):
        """Initializes an Agent.

        Args:
            program (Callable, optional): The agent's program. If None, a
                default program that does nothing is used.
        """
        self.alive = True
        self.bump = False
        self.holding = set()
        self.performance = 0

        if program is None or not isinstance(program, Callable):
            self.program = lambda percept, time: Action.NOOP
        else:
            self.program = program

    def __repr__(self):
        """Return a string representation of the Agent."""
        if self.alive:
            return super().__repr__()
        else:
            return f"#{super().__repr__()}"


class Explorer(Agent):
    """An agent that explores the Wumpus World.

    Attributes:
        position (Position): The agent's current position and orientation.
        holding (set[Thing]): The set of things the agent is holding.
        killed_by (str): The name of the thing that killed the agent.
        visited (set): A set of locations the agent has visited.
        in_world (bool): Whether the agent is still in the world.
    """

    def __init__(self, program=None):
        """Initializes an Explorer agent.

        Args:
            program (Callable, optional): The agent's program.
        """
        super().__init__(program)
        self.position = Position()  # Default position at (0, 0) facing East
        self.holding: set[Thing] = {Arrow()}
        self.killed_by = ""
        self.visited = set()
        self.in_world = True

    @property
    def has_arrow(self):
        """bool: True if the agent is holding an arrow."""
        return any(isinstance(thing, Arrow) for thing in self.holding)

    @has_arrow.setter
    def has_arrow(self, value):
        """Sets the agent's arrow status."""
        if value:
            self.holding.add(Arrow())
        else:
            self.holding = {
                thing for thing in self.holding if not isinstance(thing, Arrow)
            }

    @property
    def has_gold(self):
        """bool: True if the agent is holding gold."""
        return any(isinstance(thing, Gold) for thing in self.holding)

    def grab_gold(self, thing):
        """Grab gold if present at the agent's location.

        Args:
            thing (Thing): The thing to grab.
        """
        self.holding.add(thing) if isinstance(thing, Gold) else None


class Wumpus(Agent):
    """The Wumpus, a creature in the Wumpus World.

    Attributes:
        screamed (bool): Whether the Wumpus has screamed (after being killed).
    """
    screamed = False
    pass


class SmartWumpus(Wumpus):
    """A more intelligent version of the Wumpus."""

    def __init__(self):
        """Initializes a SmartWumpus."""
        super().__init__(self.execute)

    def execute(self, percept, time):
        """The Smart Wumpus's action program.

        The Wumpus will kill an explorer in the same location, or move
        periodically.

        Args:
            percept (dict): The current percepts for the Wumpus.
            time (int): The current time step.

        Returns:
            Action: The action to be taken by the Wumpus.
        """
        if percept.get("explorer", False):
            return Action.KILL

        if time > 0 and time % 5 == 0:
            return Action.MOVE  # Wumpus can move every 5 time steps

        return Action.NOOP  # No operation if no action is needed


class Gold(Thing):
    """Gold in the Wumpus World."""
    pass


class Pit(Thing):
    """A pit in the Wumpus World."""
    pass


class Glitter(Thing):
    """A glitter percept, indicating the presence of gold."""
    pass


class Breeze(Thing):
    """A breeze percept, indicating the presence of a nearby pit."""
    pass


class Stench(Thing):
    """A stench percept, indicating the presence of a nearby Wumpus."""
    pass


class Arrow(Thing):
    """An arrow that can be used by the Explorer."""
    pass
