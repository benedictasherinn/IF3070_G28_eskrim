import math


def violations(state):
    """Kembalikan (overlap_cells, out_of_bounds, excess_weight)."""
    sh = state.problem.ship
    seen = {}
    oob = 0
    for vid in state.inside():
        for x, y in state.cells(vid):
            if 0 <= x < sh.cols and 0 <= y < sh.rows:
                seen[(x, y)] = seen.get((x, y), 0) + 1
            else:
                oob += 1
    overlap = sum(c - 1 for c in seen.values() if c > 1)
    excess = max(0, state.weight() - sh.cap)
    return overlap, oob, excess


def violation_units(state):
    o, b, e = violations(state)
    return o + b + math.ceil(e)


def is_valid(state):
    return violation_units(state) == 0

class Objective:
    def __init__(self, problem):
        self.problem = problem
        self.penalty = sum(v.fee for v in problem.vehicles) + 1   # P besar

    def value(self, state):
        return state.fee() - self.penalty * violation_units(state)
