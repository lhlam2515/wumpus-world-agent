"""Perception module for Wumpus World Agent.

This module defines the data structures for representing agent perceptions
and available actions in the Wumpus World environment.
"""

from enum import Enum
from dataclasses import dataclass


@dataclass
class Percept:
    """Stores boolean flags for current percepts in the Wumpus World.

    This class represents the sensory information that the agent receives
    at each time step, including environmental cues about nearby hazards
    and objectives.

    Attributes:
        breeze: True if there's a breeze (indicates nearby pit).
        stench: True if there's a stench (indicates nearby wumpus).
        glitter: True if there's glitter (indicates gold in current cell).
        bump: True if agent bumped into wall during last move.
        scream: True if wumpus was killed by arrow.
    """
    breeze: bool
    stench: bool
    glitter: bool
    bump: bool
    scream: bool


class Action(Enum):
    """Available actions for the Wumpus World agent.

    This enumeration defines all possible actions that the agent can
    perform in the environment, following standard Wumpus World rules.

    **Action Descriptions:**

    - **MOVE_FORWARD**: Move one cell forward in current direction.
      * Fails silently if blocked by wall (sets bump percept)
      * May result in death if moving into pit or live wumpus
      * Updates agent position if successful

    - **TURN_LEFT**: Turn 90 degrees counterclockwise.
      * Always succeeds, no failure conditions
      * Changes orientation: North→West→South→East→North
      * No position change or hazard interactions

    - **TURN_RIGHT**: Turn 90 degrees clockwise.
      * Always succeeds, no failure conditions  
      * Changes orientation: North→East→South→West→North
      * No position change or hazard interactions

    - **SHOOT**: Fire arrow in current direction.
      * Consumes agent's arrow (one-time use)
      * Arrow travels until hitting wall or wumpus
      * Kills wumpus if hit, produces scream percept
      * No effect if agent has no arrow

    - **GRAB**: Pick up gold if present in current cell.
      * Only works if gold is in agent's current cell
      * Updates agent inventory and removes gold from world
      * No effect if no gold present

    - **CLIMB**: Exit the cave (only valid at entrance).
      * Only succeeds if agent is at starting position (0,0)
      * Ends the game with success/failure based on gold possession
      * No effect if not at cave entrance
    """
    MOVE_FORWARD = 1
    TURN_LEFT = 2
    TURN_RIGHT = 3
    SHOOT = 4
    GRAB = 5
    CLIMB = 6
