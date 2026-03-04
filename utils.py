"""Shared utilities for task scheduling algorithms."""

import json
import random
from pathlib import Path
from collections import defaultdict, deque
from typing import List, Dict, Set, Tuple

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def load_machines(path: Path) -> Tuple[List[str], List[dict]]:
    """Load machine IDs and full machine objects from JSON."""
    with open(path, 'r', encoding='utf-8') as f:
        machines = json.load(f)
    machine_ids = [m['id'] for m in machines]
    return machine_ids, machines


def load_tasks(path: Path) -> Dict[int, dict]:
    """Load tasks into a dict keyed by task ID."""
    with open(path, 'r', encoding='utf-8') as f:
        tasks = json.load(f)
    return {int(t['id']): t for t in tasks}


def compute_predecessors(tasks_dict: Dict[int, dict]) -> Tuple[Dict[int, Set[int]], Dict[int, List[int]]]:
    """Compute predecessor sets and successor lists for all tasks."""
    pred_map: Dict[int, Set[int]] = {}
    succ_map: Dict[int, List[int]] = defaultdict(list)
    for tid, t in tasks_dict.items():
        preds = set(int(p) for p in t.get('predecessors', []))
        pred_map[tid] = preds
        for p in preds:
            succ_map[p].append(tid)
    return pred_map, dict(succ_map)


def precedence_repair(order: List[int], pred_map: Dict[int, Set[int]],
                      succ_map: Dict[int, List[int]]) -> List[int]:
    """Repair an order to respect all precedence constraints (topological sort)."""
    placed: Set[int] = set()
    result: List[int] = []
    in_degree = {tid: len(pred_map.get(tid, set())) for tid in order}
    remaining = deque(order)

    while remaining:
        progressed = False
        for _ in range(len(remaining)):
            tid = remaining.popleft()
            if in_degree.get(tid, 0) == 0:
                result.append(tid)
                placed.add(tid)
                progressed = True
                for succ in succ_map.get(tid, []):
                    if succ not in placed and succ in in_degree:
                        in_degree[succ] -= 1
            else:
                remaining.append(tid)
        if not progressed and remaining:
            tid = remaining.popleft()
            result.append(tid)
            placed.add(tid)

    return result


def random_valid_order(task_ids: List[int], pred_map: Dict[int, Set[int]],
                       succ_map: Dict[int, List[int]]) -> List[int]:
    """Generate a random task order that respects precedence."""
    shuffled = task_ids[:]
    random.shuffle(shuffled)
    return precedence_repair(shuffled, pred_map, succ_map)


def decode_schedule(tasks_dict: Dict[int, dict], machine_ids: List[str],
                    order: List[int], pred_map: Dict[int, Set[int]]) -> Tuple[List[dict], int]:
    """Simulate executing tasks in the given order, return (op_schedule, makespan)."""
    machine_avail = {mid: 0 for mid in machine_ids}
    task_end: Dict[int, int] = {}
    op_schedule: List[dict] = []

    for tid in order:
        task = tasks_dict[tid]
        # Earliest start = max end time of all predecessors
        earliest = 0
        for p in pred_map.get(tid, set()):
            earliest = max(earliest, task_end.get(p, 0))

        current = earliest
        for idx, op in enumerate(task.get('operations', [])):
            mid = str(op['machine_id'])
            dur = int(op['duration'])
            start = max(current, machine_avail.get(mid, 0))
            end = start + dur
            machine_avail[mid] = end
            current = end
            op_schedule.append({
                'task_id': tid,
                'op_index': idx,
                'machine_id': mid,
                'start': start,
                'end': end,
                'duration': dur,
            })
        task_end[tid] = current

    makespan = max(task_end.values()) if task_end else 0
    return op_schedule, makespan


def generate_gantt(op_schedule: List[dict], machine_ids: List[str],
                   title: str, out_path: Path, max_ops: int = 5000) -> None:
    """Generate and save a Gantt chart as PNG."""
    ops = op_schedule
    if len(ops) > max_ops:
        step = max(1, len(ops) // max_ops)
        ops = ops[::step]

    y_index = {m: i for i, m in enumerate(machine_ids)}
    time_max = max((op['end'] for op in ops), default=1)

    fig_w = max(14, min(20, time_max / 80))
    fig_h = max(6, len(machine_ids) * 0.5 + 1)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    colors = plt.cm.tab20(np.linspace(0, 1, 20))
    for op in ops:
        mid = op['machine_id']
        tid = op['task_id']
        dur = op['end'] - op['start']
        y = y_index.get(mid, 0)
        ax.broken_barh([(op['start'], dur)], (y - 0.4, 0.8),
                       facecolors=colors[tid % 20], edgecolor='black',
                       linewidth=0.3, alpha=0.85)

    ax.set_yticks(range(len(machine_ids)))
    ax.set_yticklabels(machine_ids, fontsize=8)
    ax.set_xlabel('Time (minutes)')
    ax.set_title(title, fontweight='bold')
    ax.set_xlim(0, max(1, time_max))
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Gantt chart saved: {out_path}")


def save_results(results: dict, path: Path) -> None:
    """Save results dict to JSON (op_schedule excluded for size)."""
    to_save = {k: v for k, v in results.items() if k != 'op_schedule'}
    to_save['num_operations'] = len(results.get('op_schedule', []))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(to_save, f, indent=2)
    print(f"  Results saved: {path}")
