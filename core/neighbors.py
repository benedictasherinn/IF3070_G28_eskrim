import random
from .models import H, V


def _anchors(problem, v, ori):
    c, r = v.footprint(ori)
    sh = problem.ship
    if c > sh.cols or r > sh.rows:
        return []
    return [(x, y) for y in range(sh.rows - r + 1) for x in range(sh.cols - c + 1)]


def random_neighbor(state, rng):
    pr = state.problem
    ids = pr.ids
    new = state.copy()
    kind = rng.randint(0, 2)
    if kind == 0:    # tukar dua kendaraan
        a, b = rng.sample(ids, 2)
        new.p[a], new.p[b] = new.p[b], new.p[a]
    elif kind == 1:     # pindah / masukkan / keluarkan
        vid = rng.choice(ids)
        v = pr.by[vid]
        cur = new.p[vid]
        if cur is not None and rng.random() < 0.15:
            new.p[vid] = None    # keluarkan
        else:
            ori = cur[2] if cur else rng.choice([H, V])
            anc = _anchors(pr, v, ori)
            if anc:
                x, y = rng.choice(anc)
                new.p[vid] = (x, y, ori)
    else:   # putar
        ins = [i for i in state.inside() if not pr.by[i].square]
        if ins:
            vid = rng.choice(ins)
            x, y, ori = new.p[vid]
            new.p[vid] = (x, y, V if ori == H else H)
    return new


def all_neighbors(state):
    """Semua tetangga (untuk Steepest Ascent / Sideways)."""
    pr = state.problem
    ids = pr.ids
    out = []
    for i in range(len(ids)):      # tukar
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            if state.p[a] is None and state.p[b] is None:
                continue
            n = state.copy()
            n.p[a], n.p[b] = n.p[b], n.p[a]
            out.append(n)
    for vid in ids:      # pindah + keluarkan + putar
        v = pr.by[vid]
        cur = state.p[vid]
        oris = [cur[2]] if cur else [H, V]
        for ori in oris:
            for x, y in _anchors(pr, v, ori):
                if cur and (x, y, ori) == cur:
                    continue
                n = state.copy()
                n.p[vid] = (x, y, ori)
                out.append(n)
        if cur:
            n = state.copy()
            n.p[vid] = None
            out.append(n)
            if not v.square:
                x, y, ori = cur
                n2 = state.copy()
                n2.p[vid] = (x, y, V if ori == H else H)
                out.append(n2)
    return out
