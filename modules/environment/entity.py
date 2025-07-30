from modules.utils import Orientation
from collections.abc import Callable


class Thing:
    def __repr__(self):
        return f"{getattr(self, '__name__', self.__class__.__name__)}"

    def is_alive(self):
        """Check if the thing is alive."""
        return hasattr(self, 'alive') and self.alive  # type: ignore


class Agent(Thing):
    def __init__(self, program=None):
        self.alive = True
        self.bump = False
        self.holding = []
        self.performance = 0

        if program is None or not isinstance(program, Callable):
            print("No program provided, using default behavior.")

            self.program = lambda percept: eval(
                input(f"Percept: {percept}; action? "))
        else:
            self.program = program

    def can_grab(self, thing):
        """Check if the agent can grab the specified thing."""
        return False


class Explorer(Agent):
    def __init__(self, program=None):
        super().__init__(program)
        self.orientation = Orientation.EAST
        self.has_arrow = True
        self.visited = set()

    def can_grab(self, thing):
        """Explorer can grab gold."""
        return thing.__class__.__name__ == "Gold"
