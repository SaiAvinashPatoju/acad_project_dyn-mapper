"""
CSP Module - Constraint Satisfaction Problem modeling for Map Coloring.
"""

from .model import CSPModel
from .constraints import different_color_constraint

__all__ = ['CSPModel', 'different_color_constraint']
