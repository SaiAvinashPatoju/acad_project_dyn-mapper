"""
Map Coloring AI - Streamlit Application

A web-based interface for the AI Map Coloring System.
Supports multiple solving algorithms with performance comparison.
"""

import streamlit as st
import json
import sys
import os
import pandas as pd
import time
import tracemalloc
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from csp.model import CSPModel, DEFAULT_COLORS
from solver.backtracking import BacktrackingSolver
from solver.inference import forward_checking, ac3_inference
from solver.heuristics import (
    mrv, degree_heuristic, mrv_with_degree_tiebreaker,
    lcv, no_order
)
from visualization.plotter import GraphRenderer


# Page configuration
st.set_page_config(
    page_title="AI Map Coloring System",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
        text-align: center;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5em;
    }
    .main-header p {
        color: rgba(255,255,255,0.8);
        margin: 10px 0 0 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
        border: 1px solid #667eea44;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .success-box {
        background: linear-gradient(135deg, #27ae6022 0%, #2ecc7122 100%);
        border: 1px solid #27ae6044;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #27ae60;
    }
    .info-box {
        background: linear-gradient(135deg, #3498db22 0%, #2980b922 100%);
        border: 1px solid #3498db44;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)


def load_predefined_maps():
    """Load predefined maps from JSON file."""
    maps_path = Path(__file__).parent.parent / 'data' / 'maps.json'
    try:
        with open(maps_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Maps file not found: {maps_path}")
        return {}


def create_solver(var_heuristic: str, val_heuristic: str, 
                  inference_type: str) -> BacktrackingSolver:
    """Create a solver with specified configuration."""
    
    # Variable selection heuristic
    select_var = None
    if var_heuristic == "MRV":
        select_var = mrv
    elif var_heuristic == "Degree":
        select_var = degree_heuristic
    elif var_heuristic == "MRV + Degree":
        select_var = mrv_with_degree_tiebreaker
    
    # Value ordering heuristic
    order_val = None
    if val_heuristic == "LCV":
        order_val = lcv
    elif val_heuristic == "None":
        order_val = no_order
    
    # Inference method
    inference = None
    if inference_type == "Forward Checking":
        inference = forward_checking
    elif inference_type == "AC-3":
        inference = ac3_inference
    
    return BacktrackingSolver(
        inference=inference,
        select_variable=select_var,
        order_values=order_val
    )


def solve_and_measure(csp: CSPModel, solver: BacktrackingSolver):
    """Solve CSP and measure performance."""
    tracemalloc.start()
    start_time = time.time()
    
    solution = solver.solve(csp)
    
    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    stats = solver.get_stats()
    
    return {
        'solution': solution,
        'time': end_time - start_time,
        'memory_peak': peak / 1024 / 1024,  # Convert to MB
        'nodes': stats.nodes_explored,
        'backtracks': stats.backtracks,
        'inference_calls': stats.inference_calls,
        'pruned': stats.pruned_values
    }


def display_metrics(results: dict, col):
    """Display performance metrics in a column."""
    with col:
        st.metric("⏱️ Time", f"{results['time']*1000:.2f} ms")
        st.metric("🔍 Nodes Explored", results['nodes'])
        st.metric("↩️ Backtracks", results['backtracks'])
        st.metric("💾 Peak Memory", f"{results['memory_peak']:.3f} MB")


def main():
    """Main application function."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🗺️ AI Map Coloring System</h1>
        <p>Constraint Satisfaction Problem Solver with Visual Interface</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Map Selection
        st.subheader("📍 Map Selection")
        maps_data = load_predefined_maps()
        
        map_source = st.radio(
            "Map Source",
            ["Predefined Maps", "Custom Map (JSON)"]
        )
        
        csp = None
        
        if map_source == "Predefined Maps" and maps_data:
            map_options = {v.get('name', k): k for k, v in maps_data.items()}
            selected_name = st.selectbox("Select Map", list(map_options.keys()))
            selected_key = map_options[selected_name]
            
            if selected_key:
                maps_path = Path(__file__).parent.parent / 'data' / 'maps.json'
                csp = CSPModel.from_json(str(maps_path), selected_key)
                
                st.info(f"**Regions:** {len(csp.variables)}  \n**Constraints:** {len(csp.constraints)}")
        
        else:
            uploaded_file = st.file_uploader("Upload JSON Map", type=['json'])
            if uploaded_file:
                try:
                    map_data = json.load(uploaded_file)
                    csp = CSPModel.from_dict(map_data)
                    st.success(f"Loaded: {len(csp.variables)} regions")
                except Exception as e:
                    st.error(f"Error loading map: {e}")
        
        st.divider()
        
        # Algorithm Configuration
        st.subheader("🧠 Algorithm Settings")
        
        var_heuristic = st.selectbox(
            "Variable Selection",
            ["None", "MRV", "Degree", "MRV + Degree"],
            index=1
        )
        
        val_heuristic = st.selectbox(
            "Value Ordering",
            ["None", "LCV"],
            index=1
        )
        
        inference_type = st.selectbox(
            "Inference",
            ["None", "Forward Checking", "AC-3"],
            index=2
        )
        
        st.divider()
        
        # Color configuration
        st.subheader("🎨 Colors")
        num_colors = st.slider("Number of Colors", 2, 6, 4)
        available_colors = DEFAULT_COLORS[:num_colors]
        st.write(", ".join(available_colors))
        
        st.divider()
        
        # Solve button
        solve_button = st.button("🚀 Solve Map", type="primary", use_container_width=True)
        
        # Run comparison
        compare_button = st.button("📊 Compare All Algorithms", use_container_width=True)
    
    # Main content area
    if csp is None:
        st.markdown("""
        <div class="info-box">
            <h3>👋 Welcome!</h3>
            <p>Select a map from the sidebar to get started.</p>
            <ul>
                <li>Choose from predefined maps (Australia, USA, Europe, etc.)</li>
                <li>Or upload your own custom map in JSON format</li>
                <li>Configure the solving algorithm and click "Solve Map"</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Show expected JSON format
        with st.expander("📄 Custom Map JSON Format"):
            st.code('''
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
''', language='json')
        return
    
    # Create two columns for visualization
    col1, col2 = st.columns([1.2, 1])
    
    # Show unsolved map
    renderer = GraphRenderer(figsize=(8, 6))
    
    with col1:
        st.subheader("🗺️ Map Graph")
        fig = renderer.draw_graph(csp, title=f"{csp.name}")
        st.pyplot(fig)
    
    # Solve on button click
    if solve_button:
        with st.spinner("Solving..."):
            # Update colors if needed
            if num_colors != 4:
                csp.domains = {var: available_colors.copy() for var in csp.variables}
            
            solver = create_solver(var_heuristic, val_heuristic, inference_type)
            results = solve_and_measure(csp, solver)
        
        if results['solution']:
            with col2:
                st.subheader("✅ Solution Found!")
                
                # Display metrics
                m1, m2 = st.columns(2)
                display_metrics(results, m1)
                with m2:
                    colors_used = len(set(results['solution'].values()))
                    st.metric("🎨 Colors Used", colors_used)
                    st.metric("📝 Inference Calls", results['inference_calls'])
                    st.metric("✂️ Values Pruned", results['pruned'])
            
            # Show solved map
            with col1:
                fig_solved = renderer.draw_graph(
                    csp, 
                    assignment=results['solution'],
                    title=f"{csp.name} - Solved"
                )
                st.pyplot(fig_solved)
            
            # Show assignment table
            with st.expander("📋 Color Assignment Details"):
                df = pd.DataFrame([
                    {"Region": k, "Color": v} 
                    for k, v in sorted(results['solution'].items())
                ])
                st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.error("❌ No solution found with current configuration!")
    
    # Algorithm comparison
    if compare_button:
        st.subheader("📊 Algorithm Comparison")
        
        configs = [
            ("Backtracking Only", "None", "None", "None"),
            ("BT + FC", "None", "None", "Forward Checking"),
            ("BT + MRV", "MRV", "None", "None"),
            ("BT + MRV + LCV", "MRV", "LCV", "None"),
            ("BT + FC + MRV", "MRV", "None", "Forward Checking"),
            ("BT + AC-3 + MRV + LCV", "MRV", "LCV", "AC-3"),
        ]
        
        comparison_results = []
        progress = st.progress(0)
        
        for i, (name, var_h, val_h, inf) in enumerate(configs):
            # Reset domains for each run
            csp.domains = {var: available_colors.copy() for var in csp.variables}
            
            solver = create_solver(var_h, val_h, inf)
            results = solve_and_measure(csp, solver)
            
            comparison_results.append({
                'Algorithm': name,
                'Time (ms)': round(results['time'] * 1000, 3),
                'Nodes': results['nodes'],
                'Backtracks': results['backtracks'],
                'Memory (MB)': round(results['memory_peak'], 4),
                'Solved': '✅' if results['solution'] else '❌'
            })
            
            progress.progress((i + 1) / len(configs))
        
        progress.empty()
        
        # Display comparison table
        df_comparison = pd.DataFrame(comparison_results)
        st.dataframe(df_comparison, hide_index=True, use_container_width=True)
        
        # Bar chart for time comparison
        st.bar_chart(
            df_comparison.set_index('Algorithm')['Time (ms)'],
            use_container_width=True
        )


if __name__ == "__main__":
    main()
