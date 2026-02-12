"""
Inference Module - Constraint propagation techniques.

Implements Forward Checking and AC-3 arc consistency algorithms
for domain reduction during CSP solving.
"""

from typing import Dict, List, Tuple, Union, Set
from collections import deque

from csp.model import CSPModel


class ForwardChecking:
    """
    Forward Checking inference algorithm.
    
    After each assignment, removes inconsistent values from
    the domains of neighboring unassigned variables.
    """
    
    @staticmethod
    def infer(csp: CSPModel, variable: str, value: str,
              assignment: Dict[str, str],
              domains: Dict[str, List[str]]) -> Union[bool, int]:
        """
        Apply forward checking after assigning value to variable.
        
        Args:
            csp: CSP model
            variable: Just-assigned variable
            value: Assigned value
            assignment: Current assignment
            domains: Current domains (will be modified)
            
        Returns:
            False if domain wipeout detected, else number of pruned values
        """
        pruned = 0
        
        for neighbor in csp.get_neighbors(variable):
            if neighbor not in assignment:
                # Remove the assigned value from neighbor's domain
                if value in domains[neighbor]:
                    domains[neighbor].remove(value)
                    pruned += 1
                    
                    # Check for domain wipeout
                    if len(domains[neighbor]) == 0:
                        return False
        
        return pruned


class AC3:
    """
    AC-3 (Arc Consistency Algorithm #3).
    
    Enforces arc consistency by iteratively removing values that
    have no support in neighboring domains.
    """
    
    @staticmethod
    def get_all_arcs(csp: CSPModel) -> List[Tuple[str, str]]:
        """
        Get all arcs (directed edges) from the constraint graph.
        
        Args:
            csp: CSP model
            
        Returns:
            List of (Xi, Xj) arcs
        """
        arcs = []
        for var1, var2 in csp.constraints:
            arcs.append((var1, var2))
            arcs.append((var2, var1))
        return arcs
    
    @staticmethod
    def revise(domains: Dict[str, List[str]], 
               xi: str, xj: str) -> bool:
        """
        Revise domain of Xi to be arc-consistent with Xj.
        
        Args:
            domains: Current domains
            xi: Variable whose domain is being revised
            xj: Variable Xi must be consistent with
            
        Returns:
            True if domain of Xi was revised (reduced)
        """
        revised = False
        
        # For each value in Xi's domain
        values_to_remove = []
        for x in domains[xi]:
            # Check if there exists a value in Xj's domain that satisfies constraint
            has_support = False
            for y in domains[xj]:
                if x != y:  # Different color constraint
                    has_support = True
                    break
            
            if not has_support:
                values_to_remove.append(x)
                revised = True
        
        for x in values_to_remove:
            domains[xi].remove(x)
        
        return revised
    
    @classmethod
    def enforce(cls, csp: CSPModel, 
                domains: Dict[str, List[str]],
                assignment: Dict[str, str] = None) -> bool:
        """
        Enforce arc consistency on all arcs.
        
        Args:
            csp: CSP model
            domains: Current domains (will be modified)
            assignment: Current assignment (optional)
            
        Returns:
            True if arc consistency achieved, False if domain wipeout
        """
        # Initialize queue with all arcs
        queue = deque(cls.get_all_arcs(csp))
        
        while queue:
            xi, xj = queue.popleft()
            
            # Skip assigned variables
            if assignment and xi in assignment:
                continue
            
            if cls.revise(domains, xi, xj):
                if len(domains[xi]) == 0:
                    return False  # Domain wipeout
                
                # Add all arcs (Xk, Xi) where Xk is a neighbor of Xi (except Xj)
                for xk in csp.get_neighbors(xi):
                    if xk != xj:
                        queue.append((xk, xi))
        
        return True
    
    @classmethod
    def infer(cls, csp: CSPModel, variable: str, value: str,
              assignment: Dict[str, str],
              domains: Dict[str, List[str]]) -> Union[bool, int]:
        """
        Apply AC-3 as inference after assigning value to variable.
        
        This is called after each assignment to maintain arc consistency.
        
        Args:
            csp: CSP model
            variable: Just-assigned variable
            value: Assigned value
            assignment: Current assignment
            domains: Current domains (will be modified)
            
        Returns:
            False if domain wipeout, else number of pruned values
        """
        # Count initial domain sizes
        initial_sizes = sum(len(d) for d in domains.values())
        
        # First apply forward checking to remove immediate conflicts
        for neighbor in csp.get_neighbors(variable):
            if neighbor not in assignment and value in domains[neighbor]:
                domains[neighbor].remove(value)
                if len(domains[neighbor]) == 0:
                    return False
        
        # Then enforce full arc consistency
        if not cls.enforce(csp, domains, assignment):
            return False
        
        # Calculate pruned values
        final_sizes = sum(len(d) for d in domains.values())
        pruned = initial_sizes - final_sizes
        
        return pruned


def forward_checking(csp: CSPModel, variable: str, value: str,
                     assignment: Dict[str, str],
                     domains: Dict[str, List[str]]) -> Union[bool, int]:
    """
    Convenience function for forward checking inference.
    
    Args:
        csp: CSP model
        variable: Just-assigned variable
        value: Assigned value
        assignment: Current assignment
        domains: Current domains
        
    Returns:
        False if domain wipeout, else number of pruned values
    """
    return ForwardChecking.infer(csp, variable, value, assignment, domains)


def ac3_inference(csp: CSPModel, variable: str, value: str,
                  assignment: Dict[str, str],
                  domains: Dict[str, List[str]]) -> Union[bool, int]:
    """
    Convenience function for AC-3 inference.
    
    Args:
        csp: CSP model
        variable: Just-assigned variable
        value: Assigned value
        assignment: Current assignment
        domains: Current domains
        
    Returns:
        False if domain wipeout, else number of pruned values
    """
    return AC3.infer(csp, variable, value, assignment, domains)
