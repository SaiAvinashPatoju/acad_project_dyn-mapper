# AI Map Coloring - Benchmark Report

Performance comparison across different map sizes and algorithm configurations.

## Map: Australia
- **Regions:** 6
- **Constraints:** 9

| Algorithm             |   Time (ms) |   Nodes Explored |   Backtracks | Solved   |
|:----------------------|------------:|-----------------:|-------------:|:---------|
| Backtracking Only     |       0.333 |                6 |            0 | True     |
| BT + Forward Checking |       0.333 |                6 |            0 | True     |
| BT + AC-3             |       1.337 |                6 |            0 | True     |
| BT + MRV              |       0     |                6 |            0 | True     |
| BT + Degree Heuristic |       0.667 |                6 |            0 | True     |
| BT + MRV + LCV        |       0.333 |                6 |            0 | True     |
| BT + FC + MRV         |       0.667 |                6 |            0 | True     |
| BT + FC + MRV + LCV   |       1.333 |                6 |            0 | True     |
| BT + AC-3 + MRV + LCV |       2.243 |                6 |            0 | True     |

**Fastest:** BT + MRV (0.000 ms)

## Map: Simple 4-Node
- **Regions:** 4
- **Constraints:** 5

| Algorithm             |   Time (ms) |   Nodes Explored |   Backtracks | Solved   |
|:----------------------|------------:|-----------------:|-------------:|:---------|
| Backtracking Only     |       0     |                4 |            0 | True     |
| BT + Forward Checking |       0.333 |                4 |            0 | True     |
| BT + AC-3             |       0.506 |                4 |            0 | True     |
| BT + MRV              |       0.334 |                4 |            0 | True     |
| BT + Degree Heuristic |       0.309 |                4 |            0 | True     |
| BT + MRV + LCV        |       0.17  |                4 |            0 | True     |
| BT + FC + MRV         |       0.337 |                4 |            0 | True     |
| BT + FC + MRV + LCV   |       0     |                4 |            0 | True     |
| BT + AC-3 + MRV + LCV |       3.178 |                4 |            0 | True     |

**Fastest:** Backtracking Only (0.000 ms)

## Map: USA Simplified
- **Regions:** 10
- **Constraints:** 19

| Algorithm             |   Time (ms) |   Nodes Explored |   Backtracks | Solved   |
|:----------------------|------------:|-----------------:|-------------:|:---------|
| Backtracking Only     |       0.667 |               10 |            0 | True     |
| BT + Forward Checking |       0.333 |               10 |            0 | True     |
| BT + AC-3             |       3.511 |               10 |            0 | True     |
| BT + MRV              |       1.333 |               10 |            0 | True     |
| BT + Degree Heuristic |       2.128 |               10 |            0 | True     |
| BT + MRV + LCV        |       2.686 |               10 |            0 | True     |
| BT + FC + MRV         |       1.377 |               10 |            0 | True     |
| BT + FC + MRV + LCV   |       0.67  |               10 |            0 | True     |
| BT + AC-3 + MRV + LCV |       5.003 |               10 |            0 | True     |

**Fastest:** BT + Forward Checking (0.333 ms)

## Map: Europe Simplified
- **Regions:** 15
- **Constraints:** 28

| Algorithm             |   Time (ms) |   Nodes Explored |   Backtracks | Solved   |
|:----------------------|------------:|-----------------:|-------------:|:---------|
| Backtracking Only     |       2.666 |               15 |            0 | True     |
| BT + Forward Checking |       1.83  |               15 |            0 | True     |
| BT + AC-3             |      12.413 |               15 |            0 | True     |
| BT + MRV              |       3.508 |               15 |            0 | True     |
| BT + Degree Heuristic |       3.68  |               15 |            0 | True     |
| BT + MRV + LCV        |       4.21  |               15 |            0 | True     |
| BT + FC + MRV         |       2.186 |               15 |            0 | True     |
| BT + FC + MRV + LCV   |       2.52  |               15 |            0 | True     |
| BT + AC-3 + MRV + LCV |      13.673 |               15 |            0 | True     |

**Fastest:** BT + Forward Checking (1.830 ms)

## Map: Large Grid (5x5)
- **Regions:** 25
- **Constraints:** 40

| Algorithm             |   Time (ms) |   Nodes Explored |   Backtracks | Solved   |
|:----------------------|------------:|-----------------:|-------------:|:---------|
| Backtracking Only     |      11.234 |               25 |            0 | True     |
| BT + Forward Checking |       8.42  |               25 |            0 | True     |
| BT + AC-3             |      29.34  |               25 |            0 | True     |
| BT + MRV              |       4.779 |               25 |            0 | True     |
| BT + Degree Heuristic |       5.127 |               25 |            0 | True     |
| BT + MRV + LCV        |       4.334 |               25 |            0 | True     |
| BT + FC + MRV         |       4.567 |               25 |            0 | True     |
| BT + FC + MRV + LCV   |       9.471 |               25 |            0 | True     |
| BT + AC-3 + MRV + LCV |      29.933 |               25 |            0 | True     |

**Fastest:** BT + MRV + LCV (4.334 ms)

