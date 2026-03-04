"""Hyper-Heuristic for Job-Shop Task Scheduling."""

import random
import time
from typing import List, Dict, Set

from utils import (
    compute_predecessors, decode_schedule,
    random_valid_order, precedence_repair,
)


def run_hh(tasks_dict, machine_ids, seed=42, iterations=500):
    """
    Run a Simple Hyper-Heuristic.

    Strategy: at each iteration, randomly pick one of several low-level
    heuristics (swap, reverse segment, shift task), apply it, and keep
    the result if it improves the makespan.

    Returns a results dict with makespan, runtime, convergence, op_schedule, etc.
    """
    random.seed(seed)

    pred_map, succ_map = compute_predecessors(tasks_dict)
    task_ids = list(tasks_dict.keys())
    n = len(task_ids)

    print(f"  HH: {n} tasks, iters={iterations}")

    # --- Low-level heuristics ---
    def heuristic_swap(order):
        """Swap two random tasks."""
        out = order[:]
        i, j = random.sample(range(n), 2)
        out[i], out[j] = out[j], out[i]
        return precedence_repair(out, pred_map, succ_map)

    def heuristic_reverse(order):
        """Reverse a small random segment."""
        out = order[:]
        i = random.randint(0, n - 2)
        seg_len = random.randint(2, min(8, n - i))
        out[i:i + seg_len] = reversed(out[i:i + seg_len])
        return precedence_repair(out, pred_map, succ_map)

    def heuristic_shift(order):
        """Remove a random task and insert it elsewhere."""
        out = order[:]
        i = random.randint(0, n - 1)
        task = out.pop(i)
        j = random.randint(0, len(out))
        out.insert(j, task)
        return precedence_repair(out, pred_map, succ_map)

    heuristics = [heuristic_swap, heuristic_reverse, heuristic_shift]
    heuristic_names = ['swap', 'reverse', 'shift']
    heuristic_scores = [1.0, 1.0, 1.0]  # Track which heuristic works best

    # --- Initial solution ---
    current = random_valid_order(task_ids, pred_map, succ_map)
    _, current_cost = decode_schedule(tasks_dict, machine_ids, current, pred_map)

    best = current[:]
    best_cost = current_cost
    convergence = [best_cost]

    start = time.perf_counter()

    for it in range(iterations):
        # Pick a heuristic based on scores (roulette wheel)
        total_score = sum(heuristic_scores)
        probs = [s / total_score for s in heuristic_scores]
        idx = random.choices(range(len(heuristics)), weights=probs, k=1)[0]

        # Apply chosen heuristic
        neighbor = heuristics[idx](current)
        _, neigh_cost = decode_schedule(tasks_dict, machine_ids, neighbor, pred_map)

        # Accept if better
        if neigh_cost < current_cost:
            current = neighbor
            current_cost = neigh_cost
            # Reward this heuristic
            heuristic_scores[idx] += 1.0

            if current_cost < best_cost:
                best = current[:]
                best_cost = current_cost
        else:
            # Small penalty for failure
            heuristic_scores[idx] = max(0.1, heuristic_scores[idx] - 0.1)

        convergence.append(best_cost)

        if (it + 1) % 100 == 0:
            elapsed = time.perf_counter() - start
            scores_str = ', '.join(f'{heuristic_names[i]}={heuristic_scores[i]:.1f}'
                                   for i in range(len(heuristics)))
            print(f"    Iter {it+1}/{iterations}: Best={best_cost} ({best_cost/60:.1f}h), "
                  f"Scores=[{scores_str}], Time={elapsed:.1f}s")

    runtime = time.perf_counter() - start
    op_schedule, _ = decode_schedule(tasks_dict, machine_ids, best, pred_map)

    print(f"  HH DONE: makespan={best_cost} ({best_cost/60:.2f}h), time={runtime:.1f}s")

    return {
        'algorithm': 'HH',
        'makespan': best_cost,
        'runtime': round(runtime, 2),
        'convergence': convergence,
        'op_schedule': op_schedule,
        'order': best,
        'params': {
            'iterations': iterations, 'seed': seed,
            'heuristics': heuristic_names,
            'final_scores': {heuristic_names[i]: round(heuristic_scores[i], 1)
                             for i in range(len(heuristics))},
        },
    }
