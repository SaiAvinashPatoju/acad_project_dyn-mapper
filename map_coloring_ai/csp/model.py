"""
CSP Model - Core data structures for Constraint Satisfaction Problem.

This module defines the CSPModel class which represents a map coloring
problem as a constraint satisfaction problem.
"""

import json
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
import networkx as nx


# Default color palette for map coloring
DEFAULT_COLORS = ['Red', 'Green', 'Blue', 'Yellow']


@dataclass
class CSPModel:
    """
    Represents a Map Coloring CSP.
    
    Attributes:
        variables: List of region names (nodes in the map graph)
        domains: Dict mapping each variable to its available colors
        constraints: List of (var1, var2) tuples representing adjacencies
        graph: NetworkX graph representation of the map
        name: Optional name for the map
    """
    variables: List[str]
    domains: Dict[str, List[str]]
    constraints: List[Tuple[str, str]]
    graph: nx.Graph = field(default_factory=nx.Graph)
    name: str = "Unnamed Map"
    
    def __post_init__(self):
        """Build the NetworkX graph from constraints."""
        self.graph = nx.Graph()
        self.graph.add_nodes_from(self.variables)
        self.graph.add_edges_from(self.constraints)
    
    @classmethod
    def from_json(cls, json_path: str, map_key: str, 
                  colors: Optional[List[str]] = None) -> 'CSPModel':
        """
        Create a CSPModel from a JSON file.
        
        Args:
            json_path: Path to the JSON file containing map definitions
            map_key: Key of the map to load from the JSON
            colors: Optional list of colors to use (defaults to 4 colors)
            
        Returns:
            CSPModel instance
        """
        if colors is None:
            colors = DEFAULT_COLORS.copy()
            
        with open(json_path, 'r') as f:
            maps_data = json.load(f)
        
        if map_key not in maps_data:
            raise ValueError(f"Map '{map_key}' not found in {json_path}")
        
        map_data = maps_data[map_key]
        variables = map_data['regions']
        constraints = [tuple(adj) for adj in map_data['adjacencies']]
        domains = {var: colors.copy() for var in variables}
        
        return cls(
            variables=variables,
            domains=domains,
            constraints=constraints,
            name=map_data.get('name', map_key)
        )
    
    @classmethod
    def from_dict(cls, map_data: Dict, 
                  colors: Optional[List[str]] = None) -> 'CSPModel':
        """
        Create a CSPModel from a dictionary.
        
        Args:
            map_data: Dictionary with 'regions' and 'adjacencies' keys
            colors: Optional list of colors to use
            
        Returns:
            CSPModel instance
        """
        if colors is None:
            colors = DEFAULT_COLORS.copy()
            
        variables = map_data['regions']
        constraints = [tuple(adj) for adj in map_data['adjacencies']]
        domains = {var: colors.copy() for var in variables}
        
        return cls(
            variables=variables,
            domains=domains,
            constraints=constraints,
            name=map_data.get('name', 'Custom Map')
        )
    
    def get_neighbors(self, variable: str) -> List[str]:
        """
        Get all neighboring variables (adjacent regions).
        
        Args:
            variable: The variable to get neighbors for
            
        Returns:
            List of neighboring variable names
        """
        return list(self.graph.neighbors(variable))
    
    def is_consistent(self, variable: str, value: str, 
                      assignment: Dict[str, str]) -> bool:
        """
        Check if assigning value to variable is consistent with current assignment.
        
        Args:
            variable: Variable to assign
            value: Color value to assign
            assignment: Current partial assignment
            
        Returns:
            True if assignment is consistent, False otherwise
        """
        for neighbor in self.get_neighbors(variable):
            if neighbor in assignment and assignment[neighbor] == value:
                return False
        return True
    
    def is_complete(self, assignment: Dict[str, str]) -> bool:
        """
        Check if assignment is complete (all variables assigned).
        
        Args:
            assignment: Current assignment
            
        Returns:
            True if all variables are assigned
        """
        return len(assignment) == len(self.variables)
    
    def is_valid_solution(self, assignment: Dict[str, str]) -> bool:
        """
        Verify that a complete assignment is a valid solution.
        
        Args:
            assignment: Complete assignment to verify
            
        Returns:
            True if solution is valid (no conflicts)
        """
        if not self.is_complete(assignment):
            return False
            
        for var1, var2 in self.constraints:
            if assignment[var1] == assignment[var2]:
                return False
        return True
    
    def copy_domains(self) -> Dict[str, List[str]]:
        """
        Create a deep copy of the domains dictionary.
        
        Returns:
            Copy of domains dict
        """
        return {var: colors.copy() for var, colors in self.domains.items()}
    
    def __str__(self) -> str:
        """String representation of the CSP."""
        return (f"CSPModel(name='{self.name}', "
                f"variables={len(self.variables)}, "
                f"constraints={len(self.constraints)}, "
                f"colors={len(self.domains.get(self.variables[0], []))})")
    
    def __repr__(self) -> str:
        return self.__str__()
