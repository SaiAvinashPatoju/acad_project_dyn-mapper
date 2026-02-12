import pandas as pd
from pathlib import Path
from csp.model import CSPModel
from evaluation.benchmark import Benchmark

def generate_full_report():
    maps_path = Path('data/maps.json')
    import json
    with open(maps_path, 'r') as f:
        maps_data = json.load(f)
    
    report_content = "# AI Map Coloring - Benchmark Report\n\n"
    report_content += "Performance comparison across different map sizes and algorithm configurations.\n\n"
    
    for map_key in maps_data.keys():
        print(f"Benchmarking {map_key}...")
        csp = CSPModel.from_json(str(maps_path), map_key)
        benchmark = Benchmark(csp)
        benchmark.run_all(num_runs=3)
        df = benchmark.to_dataframe()
        
        report_content += f"## Map: {csp.name}\n"
        report_content += f"- **Regions:** {len(csp.variables)}\n"
        report_content += f"- **Constraints:** {len(csp.constraints)}\n\n"
        report_content += df[['Algorithm', 'Time (ms)', 'Nodes Explored', 'Backtracks', 'Solved']].to_markdown(index=False)
        report_content += "\n\n"
        
        solved = df[df['Solved'] == True]
        if not solved.empty:
            fastest = solved.loc[solved['Time (ms)'].idxmin()]
            report_content += f"**Fastest:** {fastest['Algorithm']} ({fastest['Time (ms)']:.3f} ms)\n\n"
    
    with open('BENCHMARK_REPORT.md', 'w') as f:
        f.write(report_content)
    print("Report generated: BENCHMARK_REPORT.md")

if __name__ == '__main__':
    generate_full_report()
