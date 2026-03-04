"""
Run all four scheduling algorithms (GA, SA, ACO, TABU) on tasks1000.json
and save results + Gantt charts for the dashboard.

Usage:
    cd NEWPROJECT
    python run_all.py
"""

import json
import time
from pathlib import Path

from utils import load_machines, load_tasks, generate_gantt, save_results
from ga import run_ga
from sa import run_sa
from aco import run_aco
from tabu import run_tabu


DATA_DIR = Path(__file__).parent
RESULTS_DIR = Path(__file__).parent / "results"


def main():
    RESULTS_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("  TASK SCHEDULING - ALGORITHM COMPARISON")
    print("=" * 60)

    # Load data
    machine_ids, machines_raw = load_machines(DATA_DIR / "machines.json")
    tasks_dict = load_tasks(DATA_DIR / "tasks1000.json")
    print(f"  Loaded: {len(tasks_dict)} tasks, {len(machine_ids)} machines\n")

    algorithms = [
        ("GA", run_ga),
        ("SA", run_sa),
        ("ACO", run_aco),
        ("TABU", run_tabu),
    ]

    all_results = {}

    for name, func in algorithms:
        print("-" * 60)
        print(f"  Running {name}...")
        print("-" * 60)

        result = func(tasks_dict, machine_ids)
        all_results[name] = result

        # Save individual results JSON
        save_results(result, RESULTS_DIR / f"{name.lower()}_results.json")

        # Generate Gantt chart
        generate_gantt(
            result['op_schedule'],
            machine_ids,
            title=f"{name} Schedule - Makespan: {result['makespan']} min "
                  f"({result['makespan']/60:.1f}h) - Runtime: {result['runtime']}s",
            out_path=RESULTS_DIR / f"{name.lower()}_gantt.png",
        )
        print()

    # --- Save comparison summary ---
    comparison = []
    for name, result in all_results.items():
        comparison.append({
            'algorithm': name,
            'makespan': result['makespan'],
            'makespan_hours': round(result['makespan'] / 60, 2),
            'runtime_seconds': result['runtime'],
            'num_operations': len(result['op_schedule']),
            'convergence': result.get('convergence', []),
            'params': result.get('params', {}),
        })

    comparison.sort(key=lambda x: x['makespan'])

    with open(RESULTS_DIR / 'comparison.json', 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2)

    # --- Print final summary ---
    print("=" * 60)
    print("  FINAL RESULTS")
    print("=" * 60)
    print(f"  {'Algorithm':<10} {'Makespan (min)':<16} {'Hours':<10} {'Runtime (s)':<12}")
    print("  " + "-" * 48)
    for c in comparison:
        print(f"  {c['algorithm']:<10} {c['makespan']:<16} "
              f"{c['makespan_hours']:<10.2f} {c['runtime_seconds']:<12.2f}")

    winner = comparison[0]
    print()
    print(f"  BEST: {winner['algorithm']} with {winner['makespan']} min "
          f"({winner['makespan_hours']}h)")
    print("=" * 60)
    print()
    print("  Next: run the dashboard to visualize results:")
    print("    streamlit run dashboard.py")
    print("=" * 60)


if __name__ == '__main__':
    main()
