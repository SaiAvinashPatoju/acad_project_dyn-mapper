"""
AI Map Coloring System - Main Entry Point

A CSP-based AI system that solves the Map Coloring Problem using
backtracking search with inference and heuristics.

Usage:
    python main.py                    # Run Streamlit UI
    python main.py --test             # Run tests
    python main.py --benchmark        # Run benchmark
    python main.py --solve australia  # Solve specific map
"""

import argparse
import sys
from pathlib import Path

# Set non-interactive backend for matplotlib before importing other modules that might use it
import matplotlib
matplotlib.use('Agg')

# Ensure the package is importable
sys.path.insert(0, str(Path(__file__).parent))

from csp.model import CSPModel, DEFAULT_COLORS
from solver.backtracking import BacktrackingSolver
from solver.inference import forward_checking, ac3_inference
from solver.heuristics import mrv_with_degree_tiebreaker, lcv
from visualization.plotter import GraphRenderer
from evaluation.benchmark import Benchmark, run_comparison


def run_tests():
    """Run basic tests to verify the system works."""
    print("=" * 60)
    print("AI Map Coloring System - Test Suite")
    print("=" * 60)
    
    # Test 1: CSP Model creation
    print("\n[Test 1] CSP Model Creation...")
    maps_path = Path(__file__).parent / 'data' / 'maps.json'
    csp = CSPModel.from_json(str(maps_path), 'australia')
    assert len(csp.variables) == 6, "Australia should have 6 regions"
    assert len(csp.constraints) == 9, "Australia should have 9 constraints"
    print(f"  ✓ Created CSP: {csp}")
    
    # Test 2: Basic Backtracking
    print("\n[Test 2] Basic Backtracking Solver...")
    solver = BacktrackingSolver()
    solution = solver.solve(csp)
    assert solution is not None, "Should find a solution"
    assert csp.is_valid_solution(solution), "Solution should be valid"
    print(f"  ✓ Solution found: {solution}")
    print(f"  ✓ Stats: {solver.get_stats().to_dict()}")
    
    # Test 3: Forward Checking
    print("\n[Test 3] Backtracking with Forward Checking...")
    csp.domains = {v: DEFAULT_COLORS.copy() for v in csp.variables}
    solver_fc = BacktrackingSolver(inference=forward_checking)
    solution_fc = solver_fc.solve(csp)
    assert solution_fc is not None, "FC should find a solution"
    assert csp.is_valid_solution(solution_fc), "FC solution should be valid"
    stats_fc = solver_fc.get_stats()
    print(f"  ✓ Solution found with FC")
    print(f"  ✓ Stats: nodes={stats_fc.nodes_explored}, "
          f"pruned={stats_fc.pruned_values}")
    
    # Test 4: Full solver with all optimizations
    print("\n[Test 4] Full Optimized Solver (AC-3 + MRV + LCV)...")
    csp.domains = {v: DEFAULT_COLORS.copy() for v in csp.variables}
    solver_full = BacktrackingSolver(
        inference=ac3_inference,
        select_variable=mrv_with_degree_tiebreaker,
        order_values=lcv
    )
    solution_full = solver_full.solve(csp)
    assert solution_full is not None, "Full solver should find solution"
    stats_full = solver_full.get_stats()
    print(f"  ✓ Solution found with full optimization")
    print(f"  ✓ Stats: nodes={stats_full.nodes_explored}, "
          f"time={stats_full.time_elapsed:.6f}s")
    
    # Test 5: Visualization
    print("\n[Test 5] Visualization...")
    renderer = GraphRenderer()
    fig = renderer.draw_graph(csp, assignment=solution_full)
    output_path = Path(__file__).parent / 'test_output_australia.png'
    renderer.save_figure(fig, str(output_path))
    print(f"  ✓ Graph rendered and saved to {output_path}")
    
    # Test 6: Larger map
    print("\n[Test 6] Larger Map (USA Simplified - 10 regions)...")
    csp_usa = CSPModel.from_json(str(maps_path), 'usa_simplified')
    solver_usa = BacktrackingSolver(
        inference=ac3_inference,
        select_variable=mrv_with_degree_tiebreaker,
        order_values=lcv
    )
    solution_usa = solver_usa.solve(csp_usa)
    assert solution_usa is not None, "USA map should be solvable"
    assert csp_usa.is_valid_solution(solution_usa), "USA solution should be valid"
    print(f"  ✓ USA map solved: {len(set(solution_usa.values()))} colors used")
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


def run_benchmark_cli(map_key: str = 'australia'):
    """Run benchmark from command line."""
    maps_path = Path(__file__).parent / 'data' / 'maps.json'
    csp = CSPModel.from_json(str(maps_path), map_key)
    
    benchmark = Benchmark(csp)
    benchmark.run_all(num_runs=3)
    benchmark.print_report()


def solve_map(map_key: str, show_plot: bool = True):
    """Solve a specific map and optionally show the result."""
    maps_path = Path(__file__).parent / 'data' / 'maps.json'
    csp = CSPModel.from_json(str(maps_path), map_key)
    
    print(f"Solving: {csp.name}")
    print(f"Regions: {csp.variables}")
    print(f"Constraints: {len(csp.constraints)}")
    
    solver = BacktrackingSolver(
        inference=ac3_inference,
        select_variable=mrv_with_degree_tiebreaker,
        order_values=lcv
    )
    
    solution = solver.solve(csp)
    stats = solver.get_stats()
    
    if solution:
        print(f"\n✓ Solution found!")
        print(f"  Colors used: {len(set(solution.values()))}")
        print(f"  Time: {stats.time_elapsed*1000:.3f} ms")
        print(f"  Nodes explored: {stats.nodes_explored}")
        print(f"\nAssignment:")
        for region, color in sorted(solution.items()):
            print(f"  {region}: {color}")
        
        if show_plot:
            import matplotlib.pyplot as plt
            renderer = GraphRenderer()
            fig = renderer.draw_graph(csp, assignment=solution)
            plt.show()
    else:
        print("✗ No solution found!")


def run_streamlit():
    """Launch the Streamlit UI."""
    import subprocess
    app_path = Path(__file__).parent / 'ui' / 'app.py'
    subprocess.run(['streamlit', 'run', str(app_path)])


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='AI Map Coloring System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py                    # Run Streamlit UI
  python main.py --test             # Run system tests
  python main.py --benchmark        # Run benchmark on Australia map
  python main.py --benchmark europe_simplified
  python main.py --solve australia  # Solve and display Australia map
        '''
    )
    
    parser.add_argument('--test', action='store_true',
                       help='Run system tests')
    parser.add_argument('--benchmark', nargs='?', const='australia',
                       metavar='MAP',
                       help='Run benchmark (default: australia)')
    parser.add_argument('--solve', metavar='MAP',
                       help='Solve a specific map')
    parser.add_argument('--no-plot', action='store_true',
                       help='Disable plot display for --solve')
    
    args = parser.parse_args()
    
    if args.test:
        run_tests()
    elif args.benchmark:
        run_benchmark_cli(args.benchmark)
    elif args.solve:
        solve_map(args.solve, show_plot=not args.no_plot)
    else:
        # Default: run Streamlit UI
        run_streamlit()


if __name__ == '__main__':
    main()
