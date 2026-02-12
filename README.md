# AI Map Coloring System

An AI-based system that solves the **Map Coloring Problem** using Constraint Satisfaction Problem (CSP) techniques with backtracking search, inference, and heuristics.

## 🎯 Project Overview

The Map Coloring Problem asks: Given a map divided into regions, assign colors to each region such that no two adjacent regions share the same color. This is a classic CSP that demonstrates AI search and constraint satisfaction techniques.

## 🏗️ Architecture

```
map_coloring_ai/
├── csp/                    # CSP Model & Constraints
│   ├── model.py           # CSPModel class with NetworkX graph
│   └── constraints.py     # Constraint definitions
├── solver/                 # Search Algorithms
│   ├── backtracking.py    # Recursive backtracking solver
│   ├── inference.py       # Forward Checking & AC-3
│   └── heuristics.py      # MRV, Degree, LCV
├── visualization/          # Graph Rendering
│   └── plotter.py         # Matplotlib visualization
├── ui/                     # Web Interface
│   └── app.py             # Streamlit application
├── evaluation/             # Performance Analysis
│   └── benchmark.py       # Benchmarking tools
├── data/                   # Map Data
│   └── maps.json          # Predefined maps
└── main.py                # Entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- NetworkX
- Matplotlib
- Streamlit
- Pandas

### Virtual Environment

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

### Setup

```bash
cd map_coloring_ai
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the Web UI

```bash
python main.py
# or
streamlit run ui/app.py
```

### Run Tests

```bash
python main.py --test
```

### Run Benchmark

```bash
python main.py --benchmark australia
```

### Solve a Specific Map

```bash
python main.py --solve australia
```

## 🧠 Algorithms Implemented

### Search
- **Backtracking Search**: Recursive depth-first search with constraint checking

### Inference (Constraint Propagation)
- **Forward Checking (FC)**: Reduces domains after each assignment
- **AC-3 (Arc Consistency)**: Ensures arc consistency across all constraints

### Heuristics
- **MRV (Minimum Remaining Values)**: Select variable with smallest domain
- **Degree Heuristic**: Select variable with most constraints
- **LCV (Least Constraining Value)**: Order values by least restrictions

## 📊 Performance Comparison

| Algorithm | Time | Nodes Explored | Use Case |
|-----------|------|----------------|----------|
| BT Only | High | High | Baseline |
| BT + FC | Medium | Medium | Balanced |
| BT + AC-3 + MRV + LCV | Low | Low | Optimal |

## 🗺️ Predefined Maps

- **Australia** (6 regions)
- **USA Simplified** (10 regions)
- **Europe Simplified** (15 regions)
- **Simple 4-Node** (testing)
- **Large Grid 5x5** (performance testing)

## 📝 Custom Map Format

```json
{
    "name": "My Custom Map",
    "regions": ["A", "B", "C", "D"],
    "adjacencies": [
        ["A", "B"],
        ["B", "C"],
        ["C", "D"],
        ["D", "A"]
    ]
}
```

## 📚 Tech Stack

- **Python 3.10+**
- **NetworkX** - Graph representation
- **Matplotlib** - Visualization
- **Streamlit** - Web interface
- **Pandas** - Data analysis

## 📖 Academic Reference

This project implements standard CSP solving techniques as described in:
- Russell, S., & Norvig, P. *Artificial Intelligence: A Modern Approach*

## 📄 License

MIT License - Academic project for AI course.
