# Maze Solver - Final Project

A comprehensive maze generation and pathfinding system implemented in Jack (the Nand2Tetris language). This project demonstrates advanced algorithmic concepts including procedural maze generation, A* pathfinding, and real-time visualization.

## Project Overview

This is a sophisticated maze solver that:
- **Generates** random, solvable mazes with dynamic obstacle placement
- **Solves** mazes using the A* pathfinding algorithm with Manhattan distance heuristic
- **Visualizes** the maze, obstacles, start/goal points, and the solution path in real-time
- **Validates** path solvability before confirming maze generation

The system is built entirely in Jack and compiled to VM code, demonstrating mastery of the Nand2Tetris hardware abstraction layers.

## Features

### 1. Random Maze Generation
- **Fully randomized obstacles**: 72% probability of obstacles at each cell
- **Guaranteed solvability**: Validates paths exist before accepting generated mazes
- **Boundary walls**: Solid perimeter walls contain the maze
- **Fixed entry/exit points**: Source at (1,1) and destination at (14,6)
- **Protected endpoints**: Start and goal points always remain walkable

### 2. Advanced Pathfinding
- **A* Algorithm**: Combines actual cost (g) and heuristic cost (h) for optimal pathfinding
- **Manhattan Distance Heuristic**: Calculates distance-based cost estimate
- **MinHeap Data Structure**: Efficiently manages open set with O(log n) operations
- **Visited Set Tracking**: Prevents revisiting nodes
- **Movement Costs**: Terrain-based costs (10 for empty cells, 30 for obstacles)

### 3. Visual Representation
- **Color-coded display**:
  - White: Walkable paths
  - Black: Walls and obstacles (circular visualization)
  - Black/White checkerboard: Solved path route
- **Circular obstacles**: Small circles (radius 5) represent obstacles
- **Grid-based rendering**: 16×8 grid, each cell 32×32 pixels
- **Real-time visualization**: Updates after each pathfinding operation

### 4. Statistics & Information
- **Path length**: Number of steps in the solution
- **Nodes explored**: How many cells were evaluated during pathfinding
- **Path cost**: Total movement cost of the solution
- **Display messages**: User-friendly feedback on maze status

## Project Structure

### Core Files

#### `MazeGenerator.jack`
Responsible for procedural maze generation with randomized obstacles.

**Key Methods:**
- `generateMaze()`: Main maze generation algorithm
- `random(int max)`: Pseudo-random number generator with seed-based approach

**Algorithm Details:**
1. Initialize grid with walls
2. Create walkable interior (13×5 cells)
3. Randomly place obstacles (72% probability)
4. Ensure entry/exit points are walkable
5. Validate path solvability using pathfinder
6. Remove obstacles iteratively if path not found
7. Return when solvable path exists (up to 30 attempts)

#### `Pathfinder.jack`
Implements A* pathfinding algorithm with optimal path finding.

**Key Methods:**
- `findPath(int sx, int sy, int gx, int gy)`: Execute A* algorithm
- `processNeighbor()`: Evaluate neighboring cells
- `manhattanDistance()`: Calculate heuristic cost
- `getPathLength()`: Return solution path length
- `getNodesExplored()`: Return number of evaluated cells

**Algorithm Details:**
- **f(n) = g(n) + h(n)**
  - g(n): Actual cost from start to node
  - h(n): Estimated cost from node to goal
- Uses MinHeap to always explore lowest-cost nodes first
- Tracks visited nodes to avoid cycles
- Returns true if path found, false otherwise

#### `Grid.jack`
Manages the maze grid data structure and cell properties.

**Key Methods:**
- `setTerrain(int x, int y, int terrain)`: Set cell type
- `getTerrain(int x, int y)`: Get cell type
- `isWalkable(int x, int y)`: Check if cell is passable
- `coordToIndex()` / `indexToX()` / `indexToY()`: Coordinate conversion
- `setGCost()` / `getGCost()`: Pathfinding cost storage
- `setParent()` / `getParent()`: Path reconstruction

**Grid Types:**
- `0`: Empty walkable cell
- `1`: Obstacle or wall
- `2`: Special terrain (reserved)
- `3`: Alternative terrain (reserved)

#### `MinHeap.jack`
Binary heap data structure for efficient priority queue operations.

**Key Methods:**
- `insert(int gridIndex, int fCost)`: Add node with priority
- `extractMin()`: Get and remove lowest-cost node
- `isEmpty()`: Check if heap is empty
- `clear()`: Reset heap state

**Properties:**
- Maintains min-heap property
- O(log n) insertion and extraction
- Capacity: 64 nodes
- Stores both grid indices and f-costs

#### `UI.jack`
Handles all visual rendering and user input.

**Key Methods:**
- `drawGrid()`: Render entire maze
- `drawCell()`: Render individual cell with appropriate visual
- `drawPath()`: Highlight solved path
- `handleInput()`: Process keyboard input
- `setPath()`: Configure start/goal points
- `drawMarker()`: Draw start/goal indicators

**Controls:**
- **ENTER**: Solve current maze
- **R**: Generate new maze

#### `Main.jack`
Main program loop and game state management.

**Workflow:**
1. Initialize grid, pathfinder, UI, and maze generator
2. Generate initial maze
3. Set fixed start (1,1) and goal (14,6) points
4. Display maze and instructions
5. Wait for user input
6. On ENTER: Find and display path, show statistics
7. On R: Generate new maze
8. Loop

## How It Works

### Maze Generation Flow
```
1. Create 16×8 grid filled with walls
2. Set perimeter as solid walls
3. Create walkable interior (13×5 cells)
4. Randomly mark 72% of cells as obstacles
5. Protect start (1,1) and goal (14,6) as walkable
6. REPEAT UP TO 30 TIMES:
   a. Test path from start to goal using A*
   b. If path found: DONE ✓
   c. Otherwise: Remove 30% of obstacles and retry
```

### Pathfinding (A*) Flow
```
1. Initialize open set with start node
2. WHILE open set not empty:
   a. Extract node with lowest f-cost
   b. If goal reached: SUCCESS ✓
   c. Mark node as visited
   d. FOR each neighbor (up, down, left, right):
      - Skip if visited, not walkable, or outside grid
      - Calculate tentative g-cost
      - If better than previous: update and add to open set
3. Return path by following parent pointers backward
```

### Visualization
```
Each 32×32 pixel cell displays:
- WALKABLE (0): White rectangle
- OBSTACLE (1): Black rectangle with white circle (radius 5)
- WALLS: Black rectangles
- PATH: Black/white checkerboard pattern (3×3 squares)
- START: Filled circle at (1,1)
- GOAL: Filled rectangle at (14,6)
```

## Technical Specifications

### Grid System
- **Dimensions**: 16 columns × 8 rows
- **Cell size**: 32×32 pixels
- **Display resolution**: 512×256 pixels
- **Interior space**: 13×5 walkable cells (after walls)

### Pathfinding Parameters
- **Start point**: Fixed at (1, 1)
- **Goal point**: Fixed at (14, 6)
- **Manhattan distance multiplier**: 10 (for cost calculation)
- **Movement costs**:
  - Empty cell (0): 10 units
  - Obstacle (1): 30 units
  - Unreachable: infinite

### Maze Generation Parameters
- **Obstacle probability**: 72%
- **Wall removal probability (retry)**: 30%
- **Maximum generation attempts**: 30
- **Grid capacity**: 128 cells (16×8)

### Memory Usage
- **Pathfinder arrays**: 128 elements for visited tracking
- **MinHeap capacity**: 64 nodes
- **Path storage**: 128 cell coordinates (x, y pairs)
- **Total**: ~1KB of managed memory

## Compilation & Execution

### Prerequisites
- Jack compiler (from Nand2Tetris tools)
- JVM capable of running Nand2Tetris VM
- Display capable of 512×256 resolution

### Compilation
```bash
cd /path/to/Final-project
/path/to/tools/JackCompiler.sh .
```

### Execution
```bash
/path/to/tools/VMEmulator.sh
# Load the generated VM files from the Final-project directory
# Run the program
```

### Output
- Maze display on screen
- Status messages at bottom
- Real-time path visualization after solving
- Statistics display (Steps, Explored nodes, Cost)

## Algorithm Complexity

### Maze Generation
- **Time**: O(n × m × attempts) where n=columns, m=rows
  - Grid initialization: O(n × m)
  - Obstacle placement: O(n × m)
  - Path validation: O(30 × pathfinding)
  - Typical: O(30 × A* complexity)
- **Space**: O(n × m) for grid storage

### A* Pathfinding
- **Time**: O(n × m × log(open_set_size))
  - Open set operations: O(log 64) ≈ O(1)
  - Per node: check 4 neighbors
  - Worst case: all cells visited = O(n × m)
- **Space**: O(n × m) for visited set + O(log n × m) for heap

### Path Extraction
- **Time**: O(N)
- **Space**: O(N) for path storage

## Design Decisions

### 1. A* Algorithm Choice
- Better than Dijkstra's: Uses heuristic for faster convergence
- Better than BFS: Weighted for optimal path with variable costs
- Manhattan distance: Perfect for grid-based movement

### 2. MinHeap Implementation
- Efficient priority queue for open set management
- Log-time complexity maintains algorithm efficiency
- Fixed capacity (64) sufficient for 128-cell grid

### 3. Guaranteed Solvability
- Ensures every generated maze has a valid solution
- Up to 30 retry attempts with progressive obstacle removal
- Protects start/goal points from obstacles

### 4. Color Scheme
- High contrast between walkable and blocked areas
- Distinct visual for solution path
- Intuitive: dark = obstacles, light = walkable

### 5. Fixed Entry/Exit Points
- (1,1) to (14,6) creates balanced challenge
- Far enough apart for interesting paths
- Away from corners for varied maze configurations

## Potential Enhancements

1. **Multiple algorithms**: Implement Dijkstra's, BFS, DFS for comparison
2. **Dynamic start/goal**: Allow user selection via cursor
3. **Difficulty levels**: Variable obstacle density
4. **Performance metrics**: Real-time algorithm comparison
5. **Path optimization**: Find multiple paths and compare
6. **Animation**: Show algorithm in action step-by-step
7. **Save/load mazes**: Store and replay solutions
8. **Network play**: Shared maze solving challenges

## Testing & Validation

### Test Cases
1. **Empty maze**: Verify straight path from start to goal
2. **Maximum obstacles**: Test pathfinding with 72% density
3. **Isolated cells**: Ensure reachability validation
4. **Edge cases**: Start/goal at boundaries (protected by design)
5. **Performance**: Large grids for algorithm efficiency

### Validation
- Every generated maze verified solvable before display
- Path reconstruction validated against parent pointers
- Statistics cross-checked with actual path traversal

## Conclusion

This maze solver demonstrates comprehensive understanding of:
- **Algorithmic problem solving** (A* pathfinding)
- **Data structures** (binary heaps, arrays)
- **Procedural generation** (random maze creation)
- **Real-time visualization** (graphics rendering)
- **System design** (modular architecture)
- **Hardware abstraction** (Jack VM platform)

The project successfully balances randomness with guaranteed solvability, optimal pathfinding with reasonable performance, and visual clarity with technical complexity.

---

**Author**: Irakli Tavadze 
**Platform**: Nand2Tetris Jack Language & VM  
**Completion Date**: January 2026  
**Status**: Complete with full feature set
