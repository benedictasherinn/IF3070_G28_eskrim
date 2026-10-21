import json
import os
from .objective import is_valid


def make_result(algorithm, objective, initial, final, history, iterations,
                duration, extra=None):
    return {
        "algorithm": algorithm,
        "initial_value": objective.value(initial),
        "final_value": objective.value(final),
        "final_valid": is_valid(final),
        "history": history,     # nilai objective per iterasi
        "iterations": iterations,
        "duration_s": round(duration, 4),
        "extra": extra or {},    # data khusus algoritma
        "initial_placements": dict(initial.p),
        "final_placements": dict(final.p),
        "initial_render": initial.render(),
        "final_render": final.render(),
    }


def summary(res):
    return (f"[{res['algorithm']}] awal={res['initial_value']} akhir={res['final_value']} "
            f"valid={res['final_valid']} iterasi={res['iterations']} durasi={res['duration_s']}s")


def save_json(res, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(res, f, indent=2)


