"""Tabu Search for Job-Shop Task Scheduling."""

import random
import time
from typing import List, Dict, Set, Tuple
from collections import deque

from utils import (
    compute_predecessors, decode_schedule,
    random_valid_order, precedence_repair,
)


def run_tabu(tasks_dict, machine_ids, seed=42, max_iters=500, tabu_tenure=15,
             n_neighbors=20):
    """
    Run Tabu Search.

    At each iteration:
      1. Generate neighbors by swapping two tasks in the current order
      2. Evaluate all neighbors
      3. Pick the best neighbor that is NOT in the tabu list
         (or that improves the global best -- aspiration criterion)
      4. Add the move to the tabu list
      5. Repeat

    Returns a results dict with makespan, runtime, convergence, op_schedule, etc.
    """
    random.seed(seed)

    pred_map, succ_map = compute_predecessors(tasks_dict)
    task_ids = list(tasks_dict.keys())
    n = len(task_ids)

    print(f"  TABU: {n} tasks, iters={max_iters}, tenure={tabu_tenure}, "
          f"neighbors={n_neighbors}")

    # --- Initial solution ---
    current = random_valid_order(task_ids, pred_map, succ_map)
    _, current_cost = decode_schedule(tasks_dict, machine_ids, current, pred_map)

    best = current[:]
    best_cost = current_cost

    # Tabu list: stores (i, j) swap pairs that are forbidden
    tabu_list: deque = deque(maxlen=tabu_tenure)
    convergence = [best_cost]

    start = time.perf_counter()

    for it in range(max_iters):
        # Generate neighbors by swapping random pairs
        best_neighbor = None
        best_neighbor_cost = float('inf')
        best_move = None

        for _ in range(n_neighbors):
            i, j = random.sample(range(n), 2)
            if i > j:
                i, j = j, i

            neighbor = current[:]
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
            neighbor = precedence_repair(neighbor, pred_map, succ_map)

            _, neigh_cost = decode_schedule(tasks_dict, machine_ids, neighbor, pred_map)

            move = (i, j)
            is_tabu = move in tabu_list

            # Accept if: (not tabu) OR (aspiration: improves global best)
            if neigh_cost < best_neighbor_cost:
                if not is_tabu or neigh_cost < best_cost:
                    best_neighbor = neighbor
                    best_neighbor_cost = neigh_cost
                    best_move = move

        # Move to best neighbor
        if best_neighbor is not None:
            current = best_neighbor
            current_cost = best_neighbor_cost
            tabu_list.append(best_move)

            if current_cost < best_cost:
                best = current[:]
                best_cost = current_cost

        convergence.append(best_cost)

        if (it + 1) % 100 == 0:
            elapsed = time.perf_counter() - start
            print(f"    Iter {it+1}/{max_iters}: Best={best_cost} ({best_cost/60:.1f}h), "
                  f"Current={current_cost}, Time={elapsed:.1f}s")

    runtime = time.perf_counter() - start
    op_schedule, _ = decode_schedule(tasks_dict, machine_ids, best, pred_map)

    print(f"  TABU DONE: makespan={best_cost} ({best_cost/60:.2f}h), time={runtime:.1f}s")

    return {
        'algorithm': 'TABU',
        'makespan': best_cost,
        'runtime': round(runtime, 2),
        'convergence': convergence,
        'op_schedule': op_schedule,
        'order': best,
        'params': {
            'max_iters': max_iters, 'tabu_tenure': tabu_tenure,
            'n_neighbors': n_neighbors, 'seed': seed,
        },
    }
