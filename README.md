# Wumpus World Agent

A Python implementation of an intelligent agent navigating through the classic AI problem environment "Wumpus World" with visualization.

## Project Overview

This project implements a Wumpus World environment with various types of agents (Hybrid Agent and Random Agent) that try to navigate a dangerous world to find gold. The environment is visualized using Pygame, allowing users to observe the agent's performance in real-time.

### What is Wumpus World?

Wumpus World is a classic AI problem where an agent navigates through a grid-based world containing:

- One or more Wumpuses (monsters that kill the agent if encountered)
- Pits (which the agent must avoid falling into)
- Gold (the treasure the agent is seeking)
- Various environmental clues like stench (near Wumpus), breeze (near pit), and glitter (near gold)

The agent must use knowledge representation, logical inference, and planning to navigate safely and find the gold.

## Features

- Interactive visualization built with Pygame
- Multiple agent implementations:
  - Hybrid Agent (using knowledge base, logical inference, and planning)
  - Random Agent (simpler movement strategy)
- Customizable world settings:
  - Adjustable grid size
  - Configurable number of Wumpuses
  - Adjustable pit probability
- Included test cases for reproducible scenarios

## Requirements

- Python 3.8+
- pygame >= 2.0.0

## Installation

1. Clone this repository:

```bash
git clone https://github.com/lhlam2515/wumpus-world-agent.git
cd wumpus-world-agent
```

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the main script to start the application:

```bash
python main.py
```

### Controls

The visualization interface has two main sections:

- Map Section: Displays the Wumpus world grid and agent's position
- Info Section: Shows controls and information about the agent's status

You can interact with the application through the interface to:

- Select different agents (Hybrid or Random)
- Choose different world configurations (Random or Predefined)
- Control the agent's actions
- Reset the world

## Project Structure

- `main.py` - Entry point for the application
- `modules/` - Core implementation modules:
  - `agent/` - Agent implementations (Hybrid and Random)
  - `environment/` - Environment and entity classes
  - `inference/` - Knowledge representation and logical inference
  - `planning/` - Path planning and problem-solving
  - `visualization/` - UI components and configuration
- `assets/` - Fonts and other resources
- `testcases/` - Predefined world configurations for testing

## How It Works

The Hybrid Agent uses:

1. Knowledge representation to keep track of visited cells and what it knows about the environment
2. Logical inference to deduce safe paths and dangerous areas
3. Planning to find optimal routes to goals or explore new areas

The agent perceives its environment, updates its knowledge base, plans its next move, and executes actions to navigate the world safely while seeking gold.

## Running Test Cases

The application includes several predefined world configurations in the `testcases/` directory. You can select these through the interface to test the agent's performance in specific scenarios.

## Acknowledgments

- Based on the Wumpus World problem as described in "Artificial Intelligence: A Modern Approach" by Stuart Russell and Peter Norvig
