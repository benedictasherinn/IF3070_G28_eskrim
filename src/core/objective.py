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
    def __init__(self, problem, mode="default"):
        """
        mode:
          - "default": fee total kendaraan terangkut (f(s) = Σ fee(v) − P·V(s))
          - "alt":     efisiensi tarif per unit luas (f(s) = Σ fee(v)/area(v) − P·V(s))
        """
        self.problem = problem
        self.mode = mode
        self.penalty = sum(v.fee for v in problem.vehicles) + 1   # P besar

    def value(self, state):
        if self.mode == "alt":
            return self._value_alt(state)
        return self._value_default(state)

    def _value_default(self, state):
        return state.fee() - self.penalty * violation_units(state)

    def _value_alt(self, state):
        """Alternatif: total rasio fee/area kendaraan terangkut."""
        total = 0.0
        for vid in state.inside():
            v = self.problem.by[vid]
            area = v.w * v.l
            if area > 0:
                total += v.fee / area
        return total - self.penalty * violation_units(state)