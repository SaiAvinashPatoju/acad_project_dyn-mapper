"""
Benchmark Module - Performance evaluation for CSP solvers.

Provides comprehensive benchmarking including time, memory,
and search statistics comparison across different algorithms.
"""

import time
import tracemalloc
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import pandas as pd

from csp.model import CSPModel, DEFAULT_COLORS
from solver.backtracking import BacktrackingSolver
from solver.inference import forward_checking, ac3_inference
from solver.heuristics import (
    mrv, degree_heuristic, mrv_with_degree_tiebreaker,
    lcv, no_order
)


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    algorithm_name: str
    time_seconds: float
    memory_peak_mb: float
    nodes_explored: int
    backtracks: int
    inference_calls: int
    pruned_values: int
    colors_used: int
    solution_found: bool
    solution: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return {
            'Algorithm': self.algorithm_name,
            'Time (s)': round(self.time_seconds, 6),
            'Time (ms)': round(self.time_seconds * 1000, 3),
            'Memory (MB)': round(self.memory_peak_mb, 4),
            'Nodes Explored': self.nodes_explored,
            'Backtracks': self.backtracks,
            'Inference Calls': self.inference_calls,
            'Pruned Values': self.pruned_values,
            'Colors Used': self.colors_used,
            'Solved': self.solution_found
        }


class Benchmark:
    """
    Benchmark runner for CSP solvers.
    
    Runs multiple algorithms on the same CSP and collects
    performance metrics for comparison.
    """
    
    # Predefined algorithm configurations
    ALGORITHMS = {
        'BT': {
            'name': 'Backtracking Only',
            'var_heuristic': None,
            'val_heuristic': None,
            'inference': None
        },
        'BT+FC': {
            'name': 'BT + Forward Checking',
            'var_heuristic': None,
            'val_heuristic': None,
            'inference': forward_checking
        },
        'BT+AC3': {
            'name': 'BT + AC-3',
            'var_heuristic': None,
            'val_heuristic': None,
            'inference': ac3_inference
        },
        'BT+MRV': {
            'name': 'BT + MRV',
            'var_heuristic': mrv,
            'val_heuristic': None,
            'inference': None
        },
        'BT+DEG': {
            'name': 'BT + Degree Heuristic',
            'var_heuristic': degree_heuristic,
            'val_heuristic': None,
            'inference': None
        },
        'BT+MRV+LCV': {
            'name': 'BT + MRV + LCV',
            'var_heuristic': mrv,
            'val_heuristic': lcv,
            'inference': None
        },
        'BT+FC+MRV': {
            'name': 'BT + FC + MRV',
            'var_heuristic': mrv,
            'val_heuristic': None,
            'inference': forward_checking
        },
        'BT+FC+MRV+LCV': {
            'name': 'BT + FC + MRV + LCV',
            'var_heuristic': mrv,
            'val_heuristic': lcv,
            'inference': forward_checking
        },
        'BT+AC3+MRV+LCV': {
            'name': 'BT + AC-3 + MRV + LCV',
            'var_heuristic': mrv_with_degree_tiebreaker,
            'val_heuristic': lcv,
            'inference': ac3_inference
        }
    }
    
    def __init__(self, csp: CSPModel):
        """
        Initialize benchmark with a CSP model.
        
        Args:
            csp: CSP model to benchmark
        """
        self.csp = csp
        self.results: List[BenchmarkResult] = []
    
    def run_single(self, algorithm_key: str, 
                   num_runs: int = 1) -> BenchmarkResult:
        """
        Run benchmark for a single algorithm.
        
        Args:
            algorithm_key: Key from ALGORITHMS dict
            num_runs: Number of runs for averaging
            
        Returns:
            BenchmarkResult with averaged metrics
        """
        if algorithm_key not in self.ALGORITHMS:
            raise ValueError(f"Unknown algorithm: {algorithm_key}")
        
        config = self.ALGORITHMS[algorithm_key]
        
        total_time = 0
        total_memory = 0
        total_nodes = 0
        total_backtracks = 0
        total_inference = 0
        total_pruned = 0
        solution = None
        
        for _ in range(num_runs):
            # Reset domains
            self.csp.domains = {v: DEFAULT_COLORS.copy() 
                               for v in self.csp.variables}
            
            # Create solver
            solver = BacktrackingSolver(
                inference=config['inference'],
                select_variable=config['var_heuristic'],
                order_values=config['val_heuristic']
            )
            
            # Measure memory
            tracemalloc.start()
            start_time = time.time()
            
            solution = solver.solve(self.csp)
            
            elapsed = time.time() - start_time
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            stats = solver.get_stats()
            
            total_time += elapsed
            total_memory += peak / 1024 / 1024
            total_nodes += stats.nodes_explored
            total_backtracks += stats.backtracks
            total_inference += stats.inference_calls
            total_pruned += stats.pruned_values
        
        # Calculate averages
        n = num_runs
        colors_used = len(set(solution.values())) if solution else 0
        
        result = BenchmarkResult(
            algorithm_name=config['name'],
            time_seconds=total_time / n,
            memory_peak_mb=total_memory / n,
            nodes_explored=total_nodes // n,
            backtracks=total_backtracks // n,
            inference_calls=total_inference // n,
            pruned_values=total_pruned // n,
            colors_used=colors_used,
            solution_found=solution is not None,
            solution=solution
        )
        
        return result
    
    def run_all(self, algorithms: List[str] = None,
                num_runs: int = 1) -> List[BenchmarkResult]:
        """
        Run benchmark for multiple algorithms.
        
        Args:
            algorithms: List of algorithm keys (None = run all)
            num_runs: Number of runs per algorithm
            
        Returns:
            List of BenchmarkResults
        """
        if algorithms is None:
            algorithms = list(self.ALGORITHMS.keys())
        
        self.results = []
        
        for algo_key in algorithms:
            result = self.run_single(algo_key, num_runs)
            self.results.append(result)
        
        return self.results
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert results to pandas DataFrame.
        
        Returns:
            DataFrame with benchmark results
        """
        if not self.results:
            return pd.DataFrame()
        
        return pd.DataFrame([r.to_dict() for r in self.results])
    
    def print_report(self):
        """Print formatted benchmark report."""
        df = self.to_dataframe()
        if df.empty:
            print("No results to display. Run benchmark first.")
            return
        
        print("\n" + "=" * 80)
        print(f"BENCHMARK REPORT: {self.csp.name}")
        print(f"Variables: {len(self.csp.variables)}, "
              f"Constraints: {len(self.csp.constraints)}")
        print("=" * 80)
        
        # Select columns for display
        display_cols = ['Algorithm', 'Time (ms)', 'Nodes Explored', 
                       'Backtracks', 'Memory (MB)', 'Solved']
        print(df[display_cols].to_string(index=False))
        
        print("=" * 80)
        
        # Find best algorithm
        solved = df[df['Solved'] == True]
        if not solved.empty:
            fastest = solved.loc[solved['Time (ms)'].idxmin()]
            print(f"Fastest solved: {fastest['Algorithm']} "
                  f"({fastest['Time (ms)']:.3f} ms)")
            
            least_nodes = solved.loc[solved['Nodes Explored'].idxmin()]
            print(f"Least nodes: {least_nodes['Algorithm']} "
                  f"({least_nodes['Nodes Explored']} nodes)")


def run_comparison(csp: CSPModel, 
                   algorithms: List[str] = None,
                   num_runs: int = 3) -> pd.DataFrame:
    """
    Convenience function to run algorithm comparison.
    
    Args:
        csp: CSP model to benchmark
        algorithms: List of algorithm keys (None = recommended set)
        num_runs: Number of runs per algorithm for averaging
        
    Returns:
        DataFrame with comparison results
    """
    if algorithms is None:
        algorithms = ['BT', 'BT+FC', 'BT+MRV', 'BT+FC+MRV', 'BT+AC3+MRV+LCV']
    
    benchmark = Benchmark(csp)
    benchmark.run_all(algorithms, num_runs)
    
    return benchmark.to_dataframe()
