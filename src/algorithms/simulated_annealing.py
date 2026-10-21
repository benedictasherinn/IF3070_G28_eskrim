import math
import random
import time

from core import random_state, random_neighbor, make_result

def simulated_annealing(problem, objective, seed=0, max_iter=30000):
    rng = random.Random(seed)
    current = random_state(problem, rng)
    current_value = objective.value(current)
    initial = current.copy()    #arsip kondisi awal
    objective_trace = [current_value]    #nilai objective per iterasi

    iteration = 0
    started_at = time.perf_counter()
    while iteration < max_iter:
        iteration += 1
        candidate = random_neighbor(current, rng)
        candidate_value = objective.value(candidate)
        if candidate_value > current_value:    # terima hanya jika lebih baik
            current, current_value = candidate, candidate_value
        objective_trace.append(current_value)

    return make_result("Simulated Annealing", objective, initial, current,
                       objective_trace, iteration, time.perf_counter() - started_at)