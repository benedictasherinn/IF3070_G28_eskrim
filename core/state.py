import string
from .models import H, V


class State:
    def __init__(self, problem, placements):
        self.problem = problem
        self.p = dict(placements)    

    def copy(self):
        return State(self.problem, self.p)

    def inside(self):
        return [i for i, pl in self.p.items() if pl is not None]

    def outside(self):
        return [i for i, pl in self.p.items() if pl is None]

    def cells(self, vid):
        """Daftar sel (x, y) yang ditempati kendaraan. Kosong kalau di luar."""
        pl = self.p[vid]
        if pl is None:
            return []
        x, y, ori = pl
        c, r = self.problem.by[vid].footprint(ori)
        return [(x + dx, y + dy) for dy in range(r) for dx in range(c)]

    def weight(self):
        return sum(self.problem.by[i].weight for i in self.inside())

    def fee(self):
        return sum(self.problem.by[i].fee for i in self.inside())

    def render(self):
        """Gambar teks geladak + daftar luar (untuk visualisasi state wajib)."""
        sh = self.problem.ship
        syms = string.ascii_uppercase + string.ascii_lowercase
        letter = {vid: syms[k % len(syms)] for k, vid in enumerate(self.problem.ids)}
        grid = [["." for _ in range(sh.cols)] for _ in range(sh.rows)]
        for vid in self.inside():
            for x, y in self.cells(vid):
                if 0 <= x < sh.cols and 0 <= y < sh.rows:
                    grid[y][x] = letter[vid] if grid[y][x] == "." else "#"
        lines = ["".join(row) for row in grid]
        lines.append("Di dalam: " + (", ".join(self.inside()) or "-"))
        lines.append("Di luar : " + (", ".join(self.outside()) or "-"))
        return "\n".join(lines)
