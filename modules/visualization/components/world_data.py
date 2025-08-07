from modules.environment.entity import Wumpus, Explorer
from modules.agent import HybridAgent
from modules.environment.wumpus_world import WumpusWorld
from .knowledge_extractor import KnowledgeExtractor


class WorldData:
    """A class to represent the world data for visualization"""

    def __init__(self, world_size=0):
        self.entities = []
        self.safe_cells = None
        self.visited_cells = None
        self.world_size = world_size
        self.knowledge_extractor = None

    def get_true_world_data(self, world: WumpusWorld):
        """Set the true world data."""
        self.world_size = world.width
        world_data = [
            [[] for _ in range(self.world_size)] for _ in range(self.world_size)
        ]
        for thing in world.things:
            y, x = thing.location
            if isinstance(thing, (Explorer, HybridAgent)):
                world_data[x][y].append(
                    {
                        "name": "Agent",
                        "properties": {
                            "orientation": (
                                thing.position.get_orientation()
                                if hasattr(thing.position, "get_orientation")
                                else "EAST"
                            ),
                            "has_gold": thing.has_gold,
                            "alive": thing.alive,
                        },
                    }
                )
            elif isinstance(thing, Wumpus):
                world_data[x][y].append(
                    {
                        "name": "Wumpus",
                        "properties": {"screamed": thing.screamed},
                    }
                )
            else:
                world_data[x][y].append(
                    {
                        "name": thing.__class__.__name__,
                        "properties": {},
                    }
                )
        self.entities = list(reversed(world_data))

    def get_agent_world_data(self, agent: HybridAgent | Explorer):
        """Set the agent's world data."""
        if not self.knowledge_extractor:
            self.knowledge_extractor = KnowledgeExtractor(agent, self.world_size)
        self.safe_cells = self.knowledge_extractor.get_safe_cells()
        self.visited_cells = self.knowledge_extractor.get_visited_cells()
        self.entities = self.knowledge_extractor.get_known_entities()
