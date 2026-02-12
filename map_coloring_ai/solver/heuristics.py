"""
Heuristics Module - Variable and value ordering heuristics.

Implements MRV, Degree Heuristic, and LCV for improved CSP solving.
"""

from typing import Dict, List, Tuple, Optional
from csp.model import CSPModel


def mrv(csp: CSPModel, assignment: Dict[str, str],
        domains: Dict[str, List[str]]) -> str:
    """
    Minimum Remaining Values (MRV) heuristic.
    
    Select the unassigned variable with the smallest domain.
    Also known as "fail-first" heuristic.
    
    Args:
        csp: CSP model
        assignment: Current assignment
        domains: Current domains
        
    Returns:
        Variable with minimum remaining values
    """
    min_values = float('inf')
    best_var = None
    
    for var in csp.variables:
        if var not in assignment:
            domain_size = len(domains[var])
            if domain_size < min_values:
                min_values = domain_size
                best_var = var
    
    return best_var


def degree_heuristic(csp: CSPModel, assignment: Dict[str, str],
                     domains: Dict[str, List[str]]) -> str:
    """
    Degree Heuristic - select variable with most constraints on unassigned variables.
    
    Chooses the variable that is involved in the most constraints
    with other unassigned variables.
    
    Args:
        csp: CSP model
        assignment: Current assignment
        domains: Current domains
        
    Returns:
        Variable with the highest degree
    """
    max_degree = -1
    best_var = None
    
    for var in csp.variables:
        if var not in assignment:
            # Count constraints with unassigned neighbors
            degree = 0
            for neighbor in csp.get_neighbors(var):
                if neighbor not in assignment:
                    degree += 1
            
            if degree > max_degree:
                max_degree = degree
                best_var = var
    
    return best_var


def mrv_with_degree_tiebreaker(csp: CSPModel, assignment: Dict[str, str],
                                domains: Dict[str, List[str]]) -> str:
    """
    MRV heuristic with degree as a tiebreaker.
    
    First selects by minimum remaining values, then breaks ties
    using the degree heuristic.
    
    Args:
        csp: CSP model
        assignment: Current assignment
        domains: Current domains
        
    Returns:
        Best variable according to MRV with degree tiebreaker
    """
    candidates = []
    min_values = float('inf')
    
    # Find all variables with minimum domain size
    for var in csp.variables:
        if var not in assignment:
            domain_size = len(domains[var])
            if domain_size < min_values:
                min_values = domain_size
                candidates = [var]
            elif domain_size == min_values:
                candidates.append(var)
    
    if len(candidates) == 1:
        return candidates[0]
    
    # Break ties with degree heuristic
    max_degree = -1
    best_var = candidates[0]
    
    for var in candidates:
        degree = sum(1 for n in csp.get_neighbors(var) if n not in assignment)
        if degree > max_degree:
            max_degree = degree
            best_var = var
    
    return best_var


def lcv(csp: CSPModel, variable: str, assignment: Dict[str, str],
        domains: Dict[str, List[str]]) -> List[str]:
    """
    Least Constraining Value (LCV) heuristic.
    
    Orders domain values by how few choices they eliminate from
    neighboring domains. Prefers values that leave maximum flexibility.
    
    Args:
        csp: CSP model
        variable: Variable to order values for
        assignment: Current assignment
        domains: Current domains
        
    Returns:
        List of values ordered by least constraining first
    """
    value_scores = []
    
    for value in domains[variable]:
        # Count how many values this eliminates from neighbors
        eliminated = 0
        for neighbor in csp.get_neighbors(variable):
            if neighbor not in assignment:
                if value in domains[neighbor]:
                    eliminated += 1
        
        value_scores.append((value, eliminated))
    
    # Sort by eliminated count (ascending - least constraining first)
    value_scores.sort(key=lambda x: x[1])
    
    return [value for value, _ in value_scores]


def no_order(csp: CSPModel, variable: str, assignment: Dict[str, str],
             domains: Dict[str, List[str]]) -> List[str]:
    """
    No value ordering - returns domain values in original order.
    
    Args:
        csp: CSP model
        variable: Variable to get values for
        assignment: Current assignment (unused)
        domains: Current domains
        
    Returns:
        List of values in original order
    """
    return domains[variable].copy()


def select_unassigned_variable(csp: CSPModel, assignment: Dict[str, str],
                                domains: Dict[str, List[str]],
                                heuristic: str = 'mrv') -> str:
    """
    Select an unassigned variable using specified heuristic.
    
    Args:
        csp: CSP model
        assignment: Current assignment
        domains: Current domains
        heuristic: One of 'none', 'mrv', 'degree', 'mrv_degree'
        
    Returns:
        Selected variable
    """
    if heuristic == 'none':
        for var in csp.variables:
            if var not in assignment:
                return var
        return None
    elif heuristic == 'mrv':
        return mrv(csp, assignment, domains)
    elif heuristic == 'degree':
        return degree_heuristic(csp, assignment, domains)
    elif heuristic == 'mrv_degree':
        return mrv_with_degree_tiebreaker(csp, assignment, domains)
    else:
        raise ValueError(f"Unknown heuristic: {heuristic}")


def order_domain_values(csp: CSPModel, variable: str,
                        assignment: Dict[str, str],
                        domains: Dict[str, List[str]],
                        heuristic: str = 'lcv') -> List[str]:
    """
    Order domain values using specified heuristic.
    
    Args:
        csp: CSP model
        variable: Variable to order values for
        assignment: Current assignment
        domains: Current domains
        heuristic: One of 'none', 'lcv'
        
    Returns:
        Ordered list of values
    """
    if heuristic == 'none':
        return no_order(csp, variable, assignment, domains)
    elif heuristic == 'lcv':
        return lcv(csp, variable, assignment, domains)
    else:
        raise ValueError(f"Unknown heuristic: {heuristic}")
