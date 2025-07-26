# Wumpus World Agent

An intelligent AI agent implementation for the classic Wumpus World problem using logical inference, path planning, and knowledge representation.

## 🎯 Project Overview

This project implements a sophisticated AI agent that navigates the dangerous Wumpus World using logical reasoning and strategic planning. The agent combines knowledge-based inference, A* pathfinding, and reactive behaviors to safely explore the environment, collect gold, and escape alive.

### Key Features

- **Hybrid Intelligent Agent**: Combines logical reasoning with path planning
- **Knowledge-Based Inference**: Uses propositional logic and formal reasoning
- **A* Path Planning**: Optimal pathfinding through safe areas
- **Real-time Visualization**: ASCII-based display of world state and agent knowledge
- **Configurable Environments**: Adjustable grid size, hazard probability, and difficulty
- **Baseline Comparison**: Random agent for performance evaluation

## 🏛️ Architecture

The project follows a modular, object-oriented design with clear separation of concerns:

```plaintext
wumpus-world-agent/
├── modules/
│   ├── agent.py           # Intelligent and random agent implementations
│   ├── environment.py     # Wumpus World simulation environment
│   ├── perception.py      # Sensory data structures and actions
│   ├── inference.py       # Knowledge base and logical inference
│   ├── planning.py        # A* pathfinding and action planning
│   ├── visualization.py   # ASCII-based world visualization
│   ├── logic.py           # Propositional logic utilities
│   └── utils.py           # Common data structures and utilities
├── main.py                # Main application entry point
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

### Core Components

#### 🤖 Agent (`modules/agent.py`)

- **Agent**: Hybrid intelligent agent with logical reasoning
- **RandomAgent**: Baseline random behavior for comparison

#### 🌍 Environment (`modules/environment.py`)

- **Environment**: Complete Wumpus World simulation
- **Cell**: Individual grid cell with hazards and objectives

#### 👁️ Perception (`modules/perception.py`)

- **Percept**: Sensory information (breeze, stench, glitter, etc.)
- **Action**: Available agent actions (move, turn, shoot, grab, climb)

#### 🧠 Inference (`modules/inference.py`)

- **KnowledgeBase**: Propositional logic knowledge representation
- **InferenceEngine**: Logical reasoning for safety and danger inference

#### 🗺️ Planning (`modules/planning.py`)

- **Planner**: A* search for optimal safe pathfinding

#### 📺 Visualization (`modules/visualization.py`)

- **Visualizer**: ASCII display of world state and agent knowledge

## 🎮 Wumpus World Rules

### Environment

- **Grid**: N×N cells with (0,0) as safe starting position
- **Hazards**: Randomly placed pits and wumpuses
- **Objective**: Single gold piece placed randomly
- **Goal**: Collect gold and return to (0,0) to exit safely

### Agent Capabilities

- **Movement**: Forward movement in current direction
- **Rotation**: Turn left or right (90-degree turns)
- **Shooting**: Fire arrow to kill wumpus (one shot only)
- **Collection**: Grab gold when in same cell
- **Exit**: Climb out at starting position

### Percepts

- **Breeze**: Felt when adjacent to pit
- **Stench**: Smelled when adjacent to live wumpus
- **Glitter**: Seen when gold is in current cell
- **Bump**: Felt when attempting to move through wall
- **Scream**: Heard when arrow kills wumpus

### Death Conditions

- Falling into a pit
- Entering cell with live wumpus
- Being eaten by wumpus

## 🧠 AI Approach

### Logical Inference

The agent uses propositional logic to reason about the world:

1. **Physics Rules**: Encodes relationships between percepts and hazards
   - `Breeze(x,y) ↔ (Pit(x-1,y) ∨ Pit(x+1,y) ∨ Pit(x,y-1) ∨ Pit(x,y+1))`
   - `Stench(x,y) ↔ (Wumpus(x-1,y) ∨ Wumpus(x+1,y) ∨ Wumpus(x,y-1) ∨ Wumpus(x,y+1))`

2. **Knowledge Updates**: Add percept information as logical facts
3. **Inference**: Use forward chaining and DPLL to derive new knowledge
4. **Safety Analysis**: Prove which cells are safe or dangerous

### Path Planning

The agent uses A* search for optimal navigation:

1. **Search Space**: Grid cells as nodes, adjacency as edges
2. **Heuristic**: Manhattan distance to goal
3. **Constraints**: Only move through provably safe cells
4. **Action Generation**: Convert position path to movement actions

### Decision Making

The agent follows a sophisticated decision cycle:

1. **Perceive**: Collect sensory information
2. **Update**: Add new facts to knowledge base
3. **Infer**: Derive safety and danger information
4. **Plan**: Generate optimal path to goals
5. **Act**: Execute next planned action

## 📊 Performance Metrics

### Success Criteria

- **Victory**: Agent collects gold and exits alive
- **Efficiency**: Minimize steps taken to complete mission
- **Safety**: Avoid death from hazards
- **Knowledge**: Maximize world understanding with minimal exploration

### Comparison Baselines

- **Random Agent**: Random action selection for baseline comparison
- **Manual Control**: Human player performance benchmarks
- **Optimal Solution**: Theoretical minimum steps for perfect information

## 🛠️ Development

### Project Status

This project contains comprehensive Google-style docstrings and architectural specifications for all components. The implementation is designed to be completed by following the detailed specifications in each module.

### Implementation Roadmap

1. **Environment Core** (`environment.py`)
   - [ ] Grid generation and hazard placement
   - [ ] Agent state tracking and action execution
   - [ ] Percept generation and game logic

2. **Logical Inference** (`inference.py`)
   - [ ] Knowledge base initialization with physics rules
   - [ ] Percept-to-logic conversion
   - [ ] Forward chaining and DPLL inference algorithms

3. **Path Planning** (`planning.py`)
   - [ ] A* search implementation
   - [ ] Action sequence generation
   - [ ] Safety-constrained navigation

4. **Agent Intelligence** (`agent.py`)
   - [ ] Main control loop and decision cycle
   - [ ] Goal management and prioritization
   - [ ] Integration of inference and planning

5. **Visualization** (`visualization.py`)
   - [ ] ASCII grid rendering
   - [ ] Agent knowledge display
   - [ ] Real-time animation support

## 📚 References

- Russell, S. & Norvig, P. "Artificial Intelligence: A Modern Approach" (Chapter 7: Logical Agents)
- Wumpus World problem specification
- Propositional logic and inference algorithms
- A* search and pathfinding techniques
