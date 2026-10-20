import random
from .models import H, V
from .state import State


def random_state(problem, rng):
    p = {}
    sh = problem.ship
    for v in problem.vehicles:
        if rng.random() < 0.4:   # sebagian dibiarkan di luar
            p[v.id] = None
            continue
        ori = rng.choice([H, V])
        c, r = v.footprint(ori)
        if c > sh.cols or r > sh.rows:
            p[v.id] = None
            continue
        x = rng.randint(0, sh.cols - c)
        y = rng.randint(0, sh.rows - r)
        p[v.id] = (x, y, ori)   # boleh tumpang tindih; penalti yang urus
    return State(problem, p)  
