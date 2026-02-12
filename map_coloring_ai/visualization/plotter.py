"""
Graph Plotter - Matplotlib visualization for map coloring.

Renders CSP graphs with colored nodes based on solution assignments.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from typing import Dict, Optional, List, Tuple
import io


# Color palette for map coloring visualization
COLOR_MAP = {
    'Red': '#E74C3C',
    'Green': '#27AE60',
    'Blue': '#3498DB',
    'Yellow': '#F1C40F',
    'Orange': '#E67E22',
    'Purple': '#9B59B6',
    'Pink': '#FF69B4',
    'Cyan': '#00BCD4'
}

# Default color for unassigned nodes
DEFAULT_COLOR = '#BDC3C7'


class GraphRenderer:
    """
    Renders CSP graphs with Matplotlib.
    
    Supports visualizing both unsolved and solved map coloring problems
    with customizable layouts and styling.
    """
    
    def __init__(self, figsize: Tuple[int, int] = (10, 8)):
        """
        Initialize the renderer.
        
        Args:
            figsize: Figure size as (width, height)
        """
        self.figsize = figsize
        self.pos = None
        
    def draw_graph(self, csp, assignment: Optional[Dict[str, str]] = None,
                   title: Optional[str] = None,
                   show_legend: bool = True,
                   layout: str = 'spring') -> plt.Figure:
        """
        Draw the CSP graph with optional coloring.
        
        Args:
            csp: CSPModel instance
            assignment: Optional color assignment dict
            title: Optional plot title
            show_legend: Whether to show color legend
            layout: Graph layout algorithm ('spring', 'circular', 'kamada_kawai')
            
        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Get layout
        self.pos = self._get_layout(csp.graph, layout)
        
        # Get node colors
        if assignment:
            node_colors = [
                COLOR_MAP.get(assignment.get(node), DEFAULT_COLOR)
                for node in csp.graph.nodes()
            ]
        else:
            node_colors = [DEFAULT_COLOR] * len(csp.graph.nodes())
        
        # Draw the graph
        nx.draw_networkx_edges(
            csp.graph, self.pos, ax=ax,
            edge_color='#7F8C8D',
            width=2,
            alpha=0.7
        )
        
        nx.draw_networkx_nodes(
            csp.graph, self.pos, ax=ax,
            node_color=node_colors,
            node_size=1500,
            edgecolors='#2C3E50',
            linewidths=2
        )
        
        nx.draw_networkx_labels(
            csp.graph, self.pos, ax=ax,
            font_size=12,
            font_weight='bold',
            font_color='white'
        )
        
        # Set title
        if title:
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        elif csp.name:
            status = "Solution" if assignment else "Unsolved"
            ax.set_title(f"{csp.name} - {status}", fontsize=16, 
                        fontweight='bold', pad=20)
        
        # Add legend if assignment exists
        if show_legend and assignment:
            self._add_legend(ax, assignment)
        
        ax.axis('off')
        plt.tight_layout()
        
        return fig
    
    def _get_layout(self, graph: nx.Graph, layout: str) -> Dict:
        """Get node positions based on layout algorithm."""
        if layout == 'spring':
            return nx.spring_layout(graph, k=2, iterations=50, seed=42)
        elif layout == 'circular':
            return nx.circular_layout(graph)
        elif layout == 'kamada_kawai':
            return nx.kamada_kawai_layout(graph)
        elif layout == 'shell':
            return nx.shell_layout(graph)
        else:
            return nx.spring_layout(graph, seed=42)
    
    def _add_legend(self, ax, assignment: Dict[str, str]):
        """Add color legend to the plot."""
        # Get unique colors used
        colors_used = set(assignment.values())
        
        patches = []
        for color_name in sorted(colors_used):
            color_code = COLOR_MAP.get(color_name, DEFAULT_COLOR)
            patch = mpatches.Patch(color=color_code, label=color_name)
            patches.append(patch)
        
        ax.legend(
            handles=patches,
            loc='upper left',
            framealpha=0.9,
            fontsize=10
        )
    
    def save_figure(self, fig: plt.Figure, filepath: str, dpi: int = 150):
        """
        Save figure to file.
        
        Args:
            fig: Figure to save
            filepath: Output file path
            dpi: Resolution in dots per inch
        """
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
    
    def get_figure_bytes(self, fig: plt.Figure, format: str = 'png') -> bytes:
        """
        Get figure as bytes for web display.
        
        Args:
            fig: Figure to convert
            format: Image format ('png', 'svg', etc.)
            
        Returns:
            Bytes representation of the figure
        """
        buf = io.BytesIO()
        fig.savefig(buf, format=format, dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        buf.seek(0)
        return buf.getvalue()
    
    def draw_comparison(self, csp, assignments: List[Tuple[str, Dict[str, str]]],
                        title: str = "Algorithm Comparison") -> plt.Figure:
        """
        Draw multiple solutions side by side for comparison.
        
        Args:
            csp: CSPModel instance
            assignments: List of (algorithm_name, assignment) tuples
            title: Overall title
            
        Returns:
            Matplotlib Figure object
        """
        n = len(assignments)
        fig, axes = plt.subplots(1, n, figsize=(5 * n, 6))
        
        if n == 1:
            axes = [axes]
        
        # Use consistent layout across all subplots
        pos = nx.spring_layout(csp.graph, k=2, seed=42)
        
        for ax, (algo_name, assignment) in zip(axes, assignments):
            # Get node colors
            if assignment:
                node_colors = [
                    COLOR_MAP.get(assignment.get(node), DEFAULT_COLOR)
                    for node in csp.graph.nodes()
                ]
            else:
                node_colors = [DEFAULT_COLOR] * len(csp.graph.nodes())
            
            nx.draw_networkx_edges(csp.graph, pos, ax=ax,
                                   edge_color='#7F8C8D', width=1.5, alpha=0.7)
            nx.draw_networkx_nodes(csp.graph, pos, ax=ax,
                                   node_color=node_colors, node_size=800,
                                   edgecolors='#2C3E50', linewidths=1.5)
            nx.draw_networkx_labels(csp.graph, pos, ax=ax,
                                    font_size=9, font_weight='bold',
                                    font_color='white')
            
            ax.set_title(algo_name, fontsize=12, fontweight='bold')
            ax.axis('off')
        
        fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        return fig
