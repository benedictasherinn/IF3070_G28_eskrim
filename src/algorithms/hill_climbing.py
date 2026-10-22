import random
import time

from core import State, random_state, random_neighbor, all_neighbors, make_result

def best_neighbor(state, objective):
    best, best_value = None, None
    for neighbor in all_neighbors(state):
        value = objective.value(neighbor)
        if best_value is None or value > best_value:
            best, best_value = neighbor, value
    return best, best_value


def best_neighbors(state, objective):
    best, best_value = [], None
    for neighbor in all_neighbors(state):
        value = objective.value(neighbor)
        if best_value is None or value > best_value:
            best, best_value = [neighbor], value
        elif value == best_value:    #nilai sama, simpan juga
            best.append(neighbor)
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


def stochastic(problem, objective, seed=0, max_iter=20000, max_fail=1000):
    rng = random.Random(seed)
    current = random_state(problem, rng)
    current_value = objective.value(current)
    initial = current.copy()
    objective_trace = [current_value]
    fail_count = 0  #gagal berturut-turut
    iteration = 0
    started_at = time.perf_counter()
    while iteration < max_iter and fail_count < max_fail:
        neighbor = random_neighbor(current, rng)
        neighbor_value = objective.value(neighbor)
        if neighbor_value > current_value:
            current, current_value = neighbor, neighbor_value
            fail_count = 0
        else:
            fail_count += 1
        iteration += 1
        objective_trace.append(current_value)
    return make_result("stochastic", objective, initial, current, objective_trace, iteration, time.perf_counter() - started_at,
        {"max_iter": max_iter, "max_fail": max_fail})


def random_restart(problem, objective, seed=0, max_restart=5, max_iter=1000):
    objective_trace = []    #gabungan dr nilai objective semua restart
    iterations_per_restart = []
    final_per_restart = []
    best = None
    started_at = time.perf_counter()
    for restart in range(max_restart + 1):
        res = steepest_ascent(problem, objective, seed=seed + restart * 1000, max_iter=max_iter)
        if restart == 0:
            initial = State(problem, res["initial_placements"])
        objective_trace.extend(res["history"])
        iterations_per_restart.append(res["iterations"])
        final_per_restart.append(res["final_value"])
        if best is None or res["final_value"] > best["final_value"]:
            best, best_restart = res, restart
    final = State(problem, best["final_placements"])
    return make_result("random restart", objective, initial, final, objective_trace, sum(iterations_per_restart), time.perf_counter() - started_at,
        {"max_restart": max_restart, "iterations_per_restart": iterations_per_restart,
         "final_per_restart": final_per_restart, "best_restart": best_restart})


def sideways_move(problem, objective, seed=0, max_sideways=50, max_iter=1000):
    rng = random.Random(seed)
    current = random_state(problem, rng)
    current_value = objective.value(current)
    initial = current.copy()
    objective_trace = [current_value]
    sideways_count = 0
    iteration = 0
    started_at = time.perf_counter()
    while iteration < max_iter:
        neighbors, neighbor_value = best_neighbors(current, objective)
        if not neighbors or neighbor_value < current_value:
            break
        if neighbor_value == current_value:    #langkah menyamping
            if sideways_count >= max_sideways:
                break
            sideways_count += 1
        current, current_value = rng.choice(neighbors), neighbor_value
        iteration += 1
        objective_trace.append(current_value)
    return make_result("sideways move", objective, initial, current, objective_trace, iteration, time.perf_counter() - started_at,
        {"max_sideways": max_sideways, "sideways_count": sideways_count})
