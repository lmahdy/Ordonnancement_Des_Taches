"""Ant Colony Optimization for Job-Shop Task Scheduling."""

import random
import time
from typing import List, Dict, Set

import numpy as np

from utils import compute_predecessors, decode_schedule


def run_aco(tasks_dict, machine_ids, seed=42, n_ants=30, iterations=100,
            evap_rate=0.3, alpha_ph=1.0, beta_ph=2.0):
    """
    Run Ant Colony Optimization.
    Returns a results dict with makespan, runtime, convergence, op_schedule, etc.
    """
    random.seed(seed)
    np.random.seed(seed)

    pred_map, succ_map = compute_predecessors(tasks_dict)
    task_ids = list(tasks_dict.keys())
    n_tasks = len(task_ids)

    print(f"  ACO: {n_tasks} tasks, ants={n_ants}, iters={iterations}")

    # Pheromone per task (higher = more desirable to schedule early)
    pheromone = np.ones(n_tasks)

    # Heuristic: inverse of total operation duration (prefer shorter tasks)
    heuristic = np.zeros(n_tasks)
    task_to_idx = {}
    for i, tid in enumerate(task_ids):
        task_to_idx[tid] = i
        total_dur = sum(op['duration'] for op in tasks_dict[tid].get('operations', []))
        heuristic[i] = 1.0 / max(total_dur, 1)

    best_order = None
    best_ms = float('inf')
    convergence = []

    start_time = time.perf_counter()

    for it in range(iterations):
        ant_solutions = []

        for _ in range(n_ants):
            # Build a solution greedily with pheromone guidance
            order: List[int] = []
            placed: Set[int] = set()

            # Initial available tasks: those with no predecessors
            available = set()
            for tid in task_ids:
                if not pred_map.get(tid, set()):
                    available.add(tid)

            for _ in range(n_tasks):
                if not available:
                    break

                avail_list = list(available)

                # Compute selection probabilities
                probs = []
                for tid in avail_list:
                    idx = task_to_idx[tid]
                    p = (pheromone[idx] ** alpha_ph) * (heuristic[idx] ** beta_ph)
                    probs.append(p)

                total = sum(probs)
                if total == 0:
                    chosen = random.choice(avail_list)
                else:
                    probs = [p / total for p in probs]
                    chosen = random.choices(avail_list, weights=probs, k=1)[0]

                order.append(chosen)
                placed.add(chosen)
                available.discard(chosen)

                # Update available: add successors whose predecessors are all placed
                for succ in succ_map.get(chosen, []):
                    if succ not in placed and pred_map.get(succ, set()).issubset(placed):
                        available.add(succ)

            # Add any remaining tasks (should not happen if graph is valid)
            for tid in task_ids:
                if tid not in placed:
                    order.append(tid)
                    placed.add(tid)

            _, ms = decode_schedule(tasks_dict, machine_ids, order, pred_map)
            ant_solutions.append((order, ms))

        # Find best ant this iteration
        ant_solutions.sort(key=lambda x: x[1])
        iter_best_order, iter_best_ms = ant_solutions[0]

        if iter_best_ms < best_ms:
            best_ms = iter_best_ms
            best_order = iter_best_order[:]
            print(f"    Iter {it+1}: NEW BEST = {best_ms} ({best_ms/60:.1f}h)")

        convergence.append(best_ms)

        # --- Pheromone update ---
        pheromone *= (1 - evap_rate)  # Evaporation

        # Deposit pheromone based on best solution quality
        deposit = 1.0 / max(best_ms, 1)
        for pos, tid in enumerate(best_order):
            idx = task_to_idx[tid]
            # Tasks placed earlier in the best solution get more pheromone
            pheromone[idx] += deposit * (n_tasks - pos) / n_tasks

        if (it + 1) % 10 == 0:
            elapsed = time.perf_counter() - start_time
            print(f"    Iter {it+1}/{iterations}: Best={best_ms} ({best_ms/60:.1f}h), "
                  f"Time={elapsed:.1f}s")

    runtime = time.perf_counter() - start_time
    op_schedule, _ = decode_schedule(tasks_dict, machine_ids, best_order, pred_map)

    print(f"  ACO DONE: makespan={best_ms} ({best_ms/60:.2f}h), time={runtime:.1f}s")

    return {
        'algorithm': 'ACO',
        'makespan': best_ms,
        'runtime': round(runtime, 2),
        'convergence': convergence,
        'op_schedule': op_schedule,
        'order': best_order,
        'params': {
            'n_ants': n_ants, 'iterations': iterations,
            'evap_rate': evap_rate, 'alpha': alpha_ph,
            'beta': beta_ph, 'seed': seed,
        },
    }
