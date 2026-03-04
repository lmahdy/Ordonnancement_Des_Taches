"""Simulated Annealing for Job-Shop Task Scheduling."""

import math
import random
import time
from typing import List, Dict, Set

from utils import (
    compute_predecessors, decode_schedule,
    random_valid_order, precedence_repair,
)


def run_sa(tasks_dict, machine_ids, seed=42, iters=2000, t0=200.0, alpha=0.995):
    """
    Run Simulated Annealing.
    Returns a results dict with makespan, runtime, convergence, op_schedule, etc.
    """
    random.seed(seed)

    pred_map, succ_map = compute_predecessors(tasks_dict)
    task_ids = list(tasks_dict.keys())

    print(f"  SA: {len(task_ids)} tasks, iters={iters}, T0={t0}, alpha={alpha}")

    # --- Initial solution ---
    current = random_valid_order(task_ids, pred_map, succ_map)
    _, current_cost = decode_schedule(tasks_dict, machine_ids, current, pred_map)

    best = current[:]
    best_cost = current_cost
    T = t0
    convergence = [best_cost]

    start = time.perf_counter()

    for it in range(iters):
        # Neighbor: swap two random positions and repair
        i, j = random.sample(range(len(current)), 2)
        neighbor = current[:]
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        neighbor = precedence_repair(neighbor, pred_map, succ_map)

        _, neigh_cost = decode_schedule(tasks_dict, machine_ids, neighbor, pred_map)
        delta = neigh_cost - current_cost

        # Accept better solutions always; worse solutions with probability exp(-delta/T)
        if delta < 0 or random.random() < math.exp(-delta / max(T, 1e-10)):
            current = neighbor
            current_cost = neigh_cost
            if current_cost < best_cost:
                best = current[:]
                best_cost = current_cost

        T *= alpha
        convergence.append(best_cost)

        if (it + 1) % 500 == 0:
            elapsed = time.perf_counter() - start
            print(f"    Iter {it+1}/{iters}: Best={best_cost} ({best_cost/60:.1f}h), "
                  f"T={T:.2f}, Time={elapsed:.1f}s")

    runtime = time.perf_counter() - start
    op_schedule, _ = decode_schedule(tasks_dict, machine_ids, best, pred_map)

    print(f"  SA DONE: makespan={best_cost} ({best_cost/60:.2f}h), time={runtime:.1f}s")

    return {
        'algorithm': 'SA',
        'makespan': best_cost,
        'runtime': round(runtime, 2),
        'convergence': convergence,
        'op_schedule': op_schedule,
        'order': best,
        'params': {
            'iters': iters, 't0': t0, 'alpha': alpha, 'seed': seed,
        },
    }
