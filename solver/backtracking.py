"""
Backtracking Solver - Core search algorithm for CSP.

Implements recursive backtracking search with optional inference
and heuristic integration.
"""

import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field

from csp.model import CSPModel


@dataclass
class SolverStats:
    """Statistics collected during solving."""
    nodes_explored: int = 0
    backtracks: int = 0
    time_elapsed: float = 0.0
    inference_calls: int = 0
    pruned_values: int = 0
    solution_found: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            'nodes_explored': self.nodes_explored,
            'backtracks': self.backtracks,
            'time_elapsed': round(self.time_elapsed, 6),
            'inference_calls': self.inference_calls,
            'pruned_values': self.pruned_values,
            'solution_found': self.solution_found
        }


class BacktrackingSolver:
    """
    Backtracking search solver for CSP.
    
    Supports optional inference (Forward Checking, AC-3) and
    variable/value ordering heuristics.
    """
    
    def __init__(self, 
                 inference: Optional[Callable] = None,
                 select_variable: Optional[Callable] = None,
                 order_values: Optional[Callable] = None,
                 use_forward_checking: bool = False,
                 use_ac3: bool = False,
                 max_nodes: int = 100000):
        """
        Initialize solver with optional enhancements.
        
        Args:
            inference: Inference function for domain reduction
            select_variable: Variable selection heuristic
            order_values: Value ordering heuristic
            use_forward_checking: Enable forward checking
            use_ac3: Enable AC-3 arc consistency
            max_nodes: Maximum nodes to explore before giving up
        """
        self.inference = inference
        self.select_variable = select_variable
        self.order_values = order_values
        self.use_forward_checking = use_forward_checking
        self.use_ac3 = use_ac3
        self.max_nodes = max_nodes
        self.stats = SolverStats()
        
    def solve(self, csp: CSPModel) -> Optional[Dict[str, str]]:
        """
        Solve the CSP using backtracking search.
        
        Args:
            csp: The CSP model to solve
            
        Returns:
            Solution assignment dict, or None if no solution
        """
        self.stats = SolverStats()
        start_time = time.time()
        
        # Make a copy of domains to avoid modifying original
        domains = csp.copy_domains()
        assignment = {}
        
        result = self._backtrack(csp, assignment, domains)
        
        self.stats.time_elapsed = time.time() - start_time
        self.stats.solution_found = result is not None
        
        return result
    
    def _backtrack(self, csp: CSPModel, assignment: Dict[str, str],
                   domains: Dict[str, List[str]]) -> Optional[Dict[str, str]]:
        """
        Recursive backtracking search.
        
        Args:
            csp: CSP model
            assignment: Current partial assignment
            domains: Current domains for each variable
            
        Returns:
            Complete assignment or None
        """
        # Node limit check
        if self.stats.nodes_explored >= self.max_nodes:
            return None

        # Check if assignment is complete
        if csp.is_complete(assignment):
            return assignment.copy()
        
        self.stats.nodes_explored += 1
        
        # Select next unassigned variable
        var = self._select_variable(csp, assignment, domains)
        
        # Get ordered domain values
        values = self._order_values(csp, var, assignment, domains)
        
        for value in values:
            if csp.is_consistent(var, value, assignment):
                # Assign value
                assignment[var] = value
                
                # Save domains for restoration
                saved_domains = {v: d.copy() for v, d in domains.items()}
                
                # Apply inference if enabled
                inference_ok = True
                if self.inference is not None:
                    inference_result = self.inference(csp, var, value, 
                                                       assignment, domains)
                    self.stats.inference_calls += 1
                    if inference_result is False:
                        inference_ok = False
                    elif isinstance(inference_result, int):
                        self.stats.pruned_values += inference_result
                
                if inference_ok:
                    result = self._backtrack(csp, assignment, domains)
                    if result is not None:
                        return result
                
                # Backtrack: undo assignment and restore domains
                del assignment[var]
                domains.update(saved_domains)
                self.stats.backtracks += 1
        
        return None
    
    def _select_variable(self, csp: CSPModel, assignment: Dict[str, str],
                         domains: Dict[str, List[str]]) -> str:
        """Select next unassigned variable."""
        if self.select_variable is not None:
            return self.select_variable(csp, assignment, domains)
        
        # Default: first unassigned variable
        for var in csp.variables:
            if var not in assignment:
                return var
        return None
    
    def _order_values(self, csp: CSPModel, variable: str,
                      assignment: Dict[str, str],
                      domains: Dict[str, List[str]]) -> List[str]:
        """Order domain values for variable."""
        if self.order_values is not None:
            return self.order_values(csp, variable, assignment, domains)
        
        # Default: use domain order
        return domains[variable].copy()
    
    def get_stats(self) -> SolverStats:
        """Get solver statistics."""
        return self.stats
