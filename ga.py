"""Genetic Algorithm for Job-Shop Task Scheduling."""

import random
import time
from typing import List, Dict, Set

import numpy as np

from utils import (
    compute_predecessors, decode_schedule,
    random_valid_order, precedence_repair,
)


# -------------------- GA Operators --------------------

def ppx_crossover(parent_a: List[int], parent_b: List[int]) -> List[int]:
    """Precedence Preserving Crossover (PPX) using binary mask."""
    n = len(parent_a)
    mask = [random.randint(0, 1) for _ in range(n)]
    child: List[int] = []
    placed: Set[int] = set()
    idx_a, idx_b = 0, 0

    for bit in mask:
        if bit == 0:
            while idx_a < n:
                t = parent_a[idx_a]
                idx_a += 1
                if t not in placed:
                    child.append(t)
                    placed.add(t)
                    break
        else:
            while idx_b < n:
                t = parent_b[idx_b]
                idx_b += 1
                if t not in placed:
                    child.append(t)
                    placed.add(t)
                    break

    # Add any remaining tasks
    for t in parent_a:
        if t not in placed:
            child.append(t)
            placed.add(t)
    return child


def mutate_swap(order: List[int], pred_map: Dict[int, Set[int]],
                succ_map: Dict[int, List[int]], rate: float = 0.2) -> List[int]:
    """Swap two random tasks; repair if it violates precedence."""
    if random.random() >= rate or len(order) < 2:
        return order
    out = order[:]
    i, j = random.sample(range(len(out)), 2)
    ti, tj = out[i], out[j]
    # If neither is predecessor of the other, swap is safe
    if tj not in pred_map.get(ti, set()) and ti not in pred_map.get(tj, set()):
        out[i], out[j] = out[j], out[i]
        return out
    # Otherwise swap + repair
    out[i], out[j] = out[j], out[i]
    return precedence_repair(out, pred_map, succ_map)


# -------------------- Main GA --------------------

def run_ga(tasks_dict, machine_ids, seed=42, pop_size=30, generations=100,
           cx_rate=0.9, mut_rate=0.2, early_stop=20):
    """
    Run the Genetic Algorithm.
    Returns a results dict with makespan, runtime, convergence, op_schedule, etc.
    """
    random.seed(seed)
    np.random.seed(seed)

    pred_map, succ_map = compute_predecessors(tasks_dict)
    task_ids = list(tasks_dict.keys())

    print(f"  GA: {len(task_ids)} tasks, pop={pop_size}, gens={generations}")

    # --- Initial population ---
    population = [random_valid_order(task_ids, pred_map, succ_map) for _ in range(pop_size)]

    def evaluate(order):
        _, ms = decode_schedule(tasks_dict, machine_ids, order, pred_map)
        return ms

    fitnesses = [evaluate(ind) for ind in population]
    scored = sorted(zip(population, fitnesses), key=lambda x: x[1])

    best_order, best_ms = scored[0]
    convergence = [best_ms]
    no_improve = 0

    t0 = time.perf_counter()

    for gen in range(generations):
        new_pop: List[List[int]] = []

        # Elitism: keep top 10%
        elite_n = max(1, pop_size // 10)
        for i in range(elite_n):
            new_pop.append(scored[i][0])

        # Fill rest via selection + crossover + mutation
        while len(new_pop) < pop_size:
            # Tournament selection (size 3)
            p1 = min(random.sample(scored, min(3, len(scored))), key=lambda x: x[1])[0]
            p2 = min(random.sample(scored, min(3, len(scored))), key=lambda x: x[1])[0]

            if random.random() < cx_rate:
                child = ppx_crossover(p1, p2)
                child = precedence_repair(child, pred_map, succ_map)
            else:
                child = p1[:]

            # Adaptive mutation: increase rate when stuck
            adaptive_rate = mut_rate * (1.5 if no_improve > 10 else 1.0)
            child = mutate_swap(child, pred_map, succ_map, adaptive_rate)

            if len(child) == len(task_ids):
                new_pop.append(child)
            else:
                new_pop.append(random_valid_order(task_ids, pred_map, succ_map))

        # Evaluate new population
        fitnesses = [evaluate(ind) for ind in new_pop]
        scored = sorted(zip(new_pop, fitnesses), key=lambda x: x[1])

        current_best = scored[0][1]
        if current_best < best_ms:
            best_ms = current_best
            best_order = scored[0][0]
            no_improve = 0
            print(f"    Gen {gen+1}: NEW BEST = {best_ms} ({best_ms/60:.1f}h)")
        else:
            no_improve += 1

        convergence.append(best_ms)

        if (gen + 1) % 20 == 0:
            elapsed = time.perf_counter() - t0
            print(f"    Gen {gen+1}/{generations}: Best={best_ms}, "
                  f"No improve={no_improve}, Time={elapsed:.1f}s")

        if no_improve >= early_stop:
            print(f"    Early stop at gen {gen+1}")
            break

    runtime = time.perf_counter() - t0
    op_schedule, _ = decode_schedule(tasks_dict, machine_ids, best_order, pred_map)

    print(f"  GA DONE: makespan={best_ms} ({best_ms/60:.2f}h), time={runtime:.1f}s")

    return {
        'algorithm': 'GA',
        'makespan': best_ms,
        'runtime': round(runtime, 2),
        'convergence': convergence,
        'op_schedule': op_schedule,
        'order': best_order,
        'params': {
            'pop_size': pop_size, 'generations': generations,
            'cx_rate': cx_rate, 'mut_rate': mut_rate, 'seed': seed,
        },
    }
