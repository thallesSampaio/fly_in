*This project has been created as part of the 42 curriculum by thasampa.*

# Fly-in

## Description

**Fly-in** is a graph-based simulation project developed in Python as part of the 42 curriculum.

The objective is to build a complete graph interpreter capable of parsing a custom configuration file, constructing a graph representation, finding optimal routes, and simulating the movement of multiple drones under different constraints.

The project also introduces weighted pathfinding, where different zone types influence route selection, encouraging drones to choose more efficient paths while respecting the simulation rules.

---

## Instructions

```bash
make run

make install
source venv/bin/activate
python main.py maps/easy/map1.txt
```
---

## Algorithm Choices

### Graph Representation

The graph is represented using:

- Zones (vertices)
- Connections (edges)

Each zone stores its neighbors and metadata such as:

- Capacity
- Zone type
- Position
- Color

Connections store:

- Maximum capacity
- Drones currently traversing them

---

### Pathfinding

The project uses **Dijkstra's algorithm** to compute the shortest weighted path.

Different zone types contribute different traversal costs:

- Priority zones receive a lower cost, encouraging the algorithm to choose them whenever possible.
- Restricted zones receive a higher cost because traversing them requires two simulation turns.
- Normal zones have the default cost.

This approach allows the routing algorithm to naturally favor more efficient paths without requiring additional heuristics.

---

### Multiple Paths

To reduce congestion, the simulator attempts to compute alternative paths.

After finding the best route, intermediate zones are temporarily blocked one at a time, forcing Dijkstra's algorithm to explore different valid paths.

The resulting routes are distributed among the drones to improve throughput.

---

### Simulation

The simulation is turn-based.

During each turn:

1. Drones already travelling through restricted connections complete their movement.
2. Available drones evaluate their next movement.
3. Capacity constraints are validated.
4. Valid movements are executed.
5. The graphical representation is updated.

---

## Visualization

The project includes an interactive visualizer built with **CustomTkinter**.

The visualization displays:

- Graph structure
- Zone types
- Zone capacities
- Connection capacities
- Drone positions
- Drones travelling through restricted connections

The simulation can be executed step-by-step using the **Next Turn** button, allowing the routing algorithm to be easily inspected and debugged.

Scrollable canvases allow large maps to be visualized without losing information.

---

## Resources

### Documentation

- Python Documentation
- CustomTkinter Documentation
- Tkinter Canvas Documentation
- Dijkstra's Algorithm
- Graph Theory

### AI Usage

Artificial intelligence (ChatGPT) was used as a development assistant for:

- brainstorming implementation ideas;
- discussing algorithm design;
- reviewing code structure;
- improving documentation;
- explaining graph algorithms;
- suggesting refactoring opportunities.

All architectural decisions, implementation, debugging, testing and final code were developed and validated by the project authors.