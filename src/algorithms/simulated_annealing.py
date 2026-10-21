import math
import random
import time

from core import random_state, random_neighbor, make_result

def boltzmann_gate(delta_e, temp):
    """Peluang penerimaan langkah memburuk"""
    if temp <= 0:
        return 0.0
    return math.exp(delta_e / temp)


def cooldown_geometric(temp, alpha):
    """Jadwal pendinginan geometrik/suhu berikutnya"""
    return temp * alpha

def simulated_annealing(problem, objective, seed=0, t0=20.0, alpha=0.999, t_min=1e-3, max_iter=30000):
    rng = random.Random(seed)
    current = random_state(problem, rng)
    current_value = objective.value(current)
    initial = current.copy()    #arsip kondisi awal
    objective_trace = [current_value]    #nilai objective per iterasi

    temp = t0
    iteration = 0
    started_at = time.perf_counter()
    while iteration < max_iter and temp > t:
        iteration += 1
        candidate = random_neighbor(current, rng)
        candidate_value = objective.value(candidate)
        delta_e = candidate_value - current_value

        if delta_e > 0:
            current, current_value = candidate, candidate_value
        else:
            prob = boltzmann_gate(delta_e, temp)
            if prob > rng.random():
                current, current_value = candidate, candidate_value
            
        objective_trace.append(current_value)
        temp = cooldown_geometric(temp, alpha)    # turunkan suhu tiap iterasi

    return make_result("Simulated Annealing", objective, initial, current, objective_trace, iteration, time.perf_counter() - started_at)