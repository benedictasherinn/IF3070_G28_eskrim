import json

H, V = "H", "V"   # orientasi: Horizontal / Vertical


class Vehicle:
    def __init__(self, id, w, l, fee, weight, eta=0):
        self.id = id
        self.w = w       # lebar
        self.l = l       # panjang
        self.fee = fee   # tarif (dimaksimalkan)
        self.weight = weight
        self.eta = eta

    def footprint(self, ori):
        """(kolom, baris) yang ditempati. V = tegak (w x l), H = diputar (l x w)."""
        return (self.w, self.l) if ori == V else (self.l, self.w)

    @property
    def square(self):
        return self.w == self.l   # persegi: diputar sama saja


class Ship:
    def __init__(self, w, l, cap):
        self.w = w
        self.l = l
        self.cap = cap    # kapasitas berat
        self.cols = w     # grid: w kolom (x) x l baris (y)
        self.rows = l


class Problem:
    def __init__(self, ship, vehicles):
        self.ship = ship
        self.vehicles = vehicles
        self.by = {v.id: v for v in vehicles}   # cari cepat dari id
        self.ids = [v.id for v in vehicles]


def load_problem(path):
    with open(path) as f:
        d = json.load(f)
    s = d["ship"]
    ship = Ship(s["dimensions"]["w"], s["dimensions"]["l"], s["max_capacity"])
    vehicles = [
        Vehicle(v["id"], v["dimensions"]["w"], v["dimensions"]["l"],
                v["shipping_fee"], v["weight"], v.get("eta", 0))
        for v in d["vehicles"]
    ]
    return Problem(ship, vehicles)
