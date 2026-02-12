"""
Constraints Module - Constraint definitions for CSP.

This module provides constraint functions used in the map coloring problem.
"""

from typing import Dict, Callable


def different_color_constraint(var1: str, val1: str, 
                                var2: str, val2: str) -> bool:
    """
    Binary constraint: Two adjacent regions must have different colors.
    
    Args:
        var1: First variable name
        val1: Color assigned to first variable
        var2: Second variable name
        val2: Color assigned to second variable
        
    Returns:
        True if constraint is satisfied (colors are different)
    """
    return val1 != val2


def create_all_diff_constraint(variables: list) -> Callable:
    """
    Create an all-different constraint for a set of variables.
    
    Args:
        variables: List of variable names that must all be different
        
    Returns:
        Constraint function
    """
    def constraint(assignment: Dict[str, str]) -> bool:
        values = [assignment[v] for v in variables if v in assignment]
        return len(values) == len(set(values))
    return constraint


def count_conflicts(assignment: Dict[str, str], 
                    constraints: list) -> int:
    """
    Count the number of constraint violations in an assignment.
    
    Args:
        assignment: Current variable assignments
        constraints: List of (var1, var2) constraint tuples
        
    Returns:
        Number of violated constraints
    """
    conflicts = 0
    for var1, var2 in constraints:
        if var1 in assignment and var2 in assignment:
            if assignment[var1] == assignment[var2]:
                conflicts += 1
    return conflicts
