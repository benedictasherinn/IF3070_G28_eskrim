import random
from .models import H, V
from .state import State


def random_state(problem, rng):
    """
    Urutkan kendaraan acak, satu per satu taruh di posisi acak yang tidak
    overlap dan tidak melebihi kapasitas berat. Yang tidak muat ditaruh di
    luar kapal (p[vid] = None)
    """
    sh = problem.ship
    placements = {v.id: None for v in problem.vehicles}
    occupied = set()
    total_weight = 0

    vehicles = list(problem.vehicles)
    rng.shuffle(vehicles)

    for v in vehicles:
        if total_weight + v.weight > sh.cap:
            continue

        oris = [H, V] if not v.square else [H]
        rng.shuffle(oris)

        placed = False
        for ori in oris:
            c, r = v.footprint(ori)
            if c > sh.cols or r > sh.rows:
                continue
            anchors = [(x, y) for y in range(sh.rows - r + 1)
                              for x in range(sh.cols - c + 1)]
            rng.shuffle(anchors)
            for x, y in anchors:
                cells = {(x + dx, y + dy) for dy in range(r) for dx in range(c)}
                if cells.isdisjoint(occupied):
                    placements[v.id] = (x, y, ori)
                    occupied.update(cells)
                    total_weight += v.weight
                    placed = True
                    break
            if placed:
                break

    return State(problem, placements)