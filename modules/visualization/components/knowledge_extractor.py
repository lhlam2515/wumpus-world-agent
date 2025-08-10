"""Knowledge extractor for visualization."""

from typing import Set, Tuple, Dict, Any
from modules.inference.logic import scream, wumpus, pit, breeze, stench, glitter, Clause


class KnowledgeExtractor:
    """Extracts visualization-relevant information from agent's knowledge base."""

    def __init__(self, agent, size=None):
        """Initialize with agent reference."""
        self.agent = agent
        self.kb = agent.kb if hasattr(agent, "kb") else None
        self.world_size = agent.size if hasattr(agent, "size") else size if size else 0
        self.gold_position = None
        self.has_arrow_previously = True
        self.hear_scream_previously = False

    def get_safe_cells(self):
        """Get all cells known to be safe."""
        return (
            set(self.agent.safe_positions)
            if hasattr(self.agent, "safe_positions")
            else None
        )

    def get_visited_cells(self):
        """Get all cells the agent has visited."""
        return set(self.agent.visited) if hasattr(self.agent, "visited") else None

    def get_known_entities(self):
        """Get all known entities from the knowledge base using bitmasks for caching."""
        entities = [
            [[] for _ in range(self.world_size)] for _ in range(self.world_size)
        ]

        if not self.kb:
            return entities

        # Check for glitter and gold position tracking first
        if (
            self.gold_position is None
            and self.agent.position
            and self.kb
            and Clause(glitter()) in self.kb
        ):
            self.gold_position = self.agent.position.location

        just_shot = not self.agent.has_arrow and self.has_arrow_previously
        self.has_arrow_previously = self.agent.has_arrow

        percept_scream = Clause(scream()) in self.kb
        just_hear_scream = percept_scream and not self.hear_scream_previously
        self.hear_scream_previously = percept_scream

        for i in range(self.world_size):
            for j in range(self.world_size):

                if Clause(wumpus(j, i)) in self.kb:
                    entities[i][j].append(
                        {
                            "name": "Wumpus",
                            "properties": {"screamed": False},
                        }
                    )

                if Clause(pit(j, i)) in self.kb:
                    entities[i][j].append({"name": "Pit", "properties": {}})

                if Clause(breeze(j, i)) in self.kb:
                    entities[i][j].append({"name": "Breeze", "properties": {}})

                if Clause(stench(j, i)) in self.kb:
                    entities[i][j].append({"name": "Stench", "properties": {}})

                if (
                    self.gold_position
                    and self.gold_position == (j, i)
                    and not self.agent.has_gold
                ):
                    entities[i][j].append({"name": "Gold", "properties": {}})

                if (
                    self.agent.in_world
                    and self.agent.position
                    and self.agent.position.location == (j, i)
                ):
                    entities[i][j].append(
                        {
                            "name": "Agent",
                            "properties": {
                                "orientation": (
                                    self.agent.position.get_orientation()
                                    if hasattr(self.agent.position, "get_orientation")
                                    else "EAST"
                                ),
                                "has_gold": self.agent.has_gold,
                                "alive": self.agent.alive,
                                "shoot_arrow": just_shot,
                                "hear_scream": just_hear_scream,
                            },
                        }
                    )

        return list(reversed(entities))

    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent's current state information."""
        info = {
            "has_gold": self.agent.has_gold,
            "has_arrow": self.agent.has_arrow,
            "alive": self.agent.alive,
            "killed_by": (
                self.agent.killed_by if hasattr(self.agent, "killed_by") else "unknown"
            ),
            "performance": self.agent.performance,
            "kb_size": len(self.kb) if self.kb else 0,
            "in_world": self.agent.in_world,
        }
        return info
