import random
import time

from core import random_state, all_neighbors, make_result

def best_neighbor(state, objective):
    best, best_value = None, None
    for neighbor in all_neighbors(state):
        value = objective.value(neighbor)
        if best_value is None or value > best_value:
            best, best_value = neighbor, value
    return best, best_value


def steepest_ascent(problem, objective, seed=0, max_iter=1000):
    rng = random.Random(seed)
    current = random_state(problem, rng)
    current_value = objective.value(current)
    initial = current.copy()
    objective_trace = [current_value]
    iteration = 0
    started_at = time.perf_counter()
    while iteration < max_iter:
        neighbor, neighbor_value = best_neighbor(current, objective)
        if neighbor is None or neighbor_value <= current_value:
            break
        current, current_value = neighbor, neighbor_value
        iteration += 1
        objective_trace.append(current_value)
    return make_result("steepest ascent", objective, initial, current, objective_trace, iteration, time.perf_counter() - started_at)