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

# Custom CSS for premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    .stApp {
        background: radial-gradient(circle at top right, #1a1a2e, #16213e);
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header optimization */
    .main-header {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 40px 20px;
        border-radius: 20px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .main-header h1 {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        font-size: 3.5em;
        font-weight: 700;
        letter-spacing: -1px;
    }
    .main-header p {
        color: #a0aec0;
        margin: 15px 0 0 0;
        font-size: 1.2em;
        font-weight: 300;
    }

    /* Cards and Glassmorphism */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 24px;
        border-radius: 16px;
        text-align: left;
        transition: all 0.3s ease;
        height: 100%;
    }
    .metric-card:hover {
        background: rgba(255, 255, 255, 0.05);
        transform: translateY(-5px);
        border-color: rgba(102, 126, 234, 0.3);
    }
    .metric-label {
        font-size: 0.9em;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 1.8em;
        font-weight: 600;
        color: #e2e8f0;
    }
    
    /* Custom Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Button Polish */
    .stButton>button {
        border-radius: 12px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.3);
    }
    .stButton>button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(118, 75, 162, 0.4);
        transform: scale(1.02);
    }

    /* Info boxes */
    .info-card {
        background: rgba(52, 152, 219, 0.1);
        border-left: 4px solid #3498db;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-in {
        animation: fadeIn 0.8s ease-out forwards;
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


def display_metrics(results: dict):
    """Display performance metrics using custom HTML cards."""
    m1, m2, m3, m4 = st.columns(4)
    
    metrics = [
        ("⏱️ Time", f"{results['time']*1000:.3f} ms"),
        ("🔍 Nodes", f"{results['nodes']:,}"),
        ("↩️ Backtracks", f"{results['backtracks']:,}"),
        ("💾 Memory", f"{results['memory_peak']:.4f} MB")
    ]
    
    cols = [m1, m2, m3, m4]
    for col, (label, value) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)


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
        <div class="animate-in">
            <div class="main-header" style="background: none; border: none; box-shadow: none;">
                <h2 style="color: #e2e8f0; font-weight: 300;">Ready to solve?</h2>
                <p>Configure your map settings in the sidebar to visualize the CSP algorithm in action.</p>
            </div>
            <div style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); display: grid; gap: 20px; margin-top: 40px;">
                <div class="metric-card">
                    <h4>📍 1. Select Map</h4>
                    <p style="color: #718096; font-size: 0.9em;">Choose from real-world examples like Australia, USA, or Europe.</p>
                </div>
                <div class="metric-card">
                    <h4>🧠 2. Pick Strategy</h4>
                    <p style="color: #718096; font-size: 0.9em;">Adjust heuristics (MRV, LCV) and inference (FC, AC-3) levels.</p>
                </div>
                <div class="metric-card">
                    <h4>🚀 3. Visualize</h4>
                    <p style="color: #718096; font-size: 0.9em;">See the solver explore the state space and find the optimal coloring.</p>
                </div>
            </div>
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
            st.markdown('<div class="animate-in">', unsafe_allow_html=True)
            st.subheader("📊 Performance Results")
            display_metrics(results)
            
            # Additional detail metrics
            m1, m2, m3 = st.columns(3)
            with m1:
                colors_used = len(set(results['solution'].values()))
                st.metric("🎨 Colors Used", colors_used)
            with m2:
                st.metric("📝 Inference Calls", f"{results['inference_calls']:,}")
            with m3:
                st.metric("✂️ Values Pruned", f"{results['pruned']:,}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
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
        
        # Enhanced comparison chart with Altair
        import altair as alt
        
        chart = alt.Chart(df_comparison).mark_bar(
            cornerRadiusTopLeft=10,
            cornerRadiusTopRight=10
        ).encode(
            x=alt.X('Algorithm:N', sort=None, axis=alt.Axis(labelAngle=-45, labelOverlap=False)),
            y=alt.Y('Time (ms):Q', title='Execution Time (ms)'),
            color=alt.Color('Algorithm:N', scale=alt.Scale(scheme='tableau20'), legend=None),
            tooltip=['Algorithm', 'Time (ms)', 'Nodes', 'Backtracks']
        ).properties(
            height=400,
            title='Algorithm Speed Comparison'
        ).configure_title(
            fontSize=20,
            font='Outfit',
            anchor='start',
            color='#e2e8f0'
        ).configure_view(strokeWidth=0)
        
        st.altair_chart(chart, use_container_width=True)


if __name__ == "__main__":
    main()
