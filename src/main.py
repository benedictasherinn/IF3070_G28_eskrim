import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import load_problem, Objective, summary, save_json
from algorithms.simulated_annealing import simulated_annealing
from algorithms.plots_sa import plot_objective, plot_acceptance, plot_states

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "output")
DATA_SMALL = os.path.join(HERE, "data", "sample_small.json")
DATA_MEDIUM = os.path.join(HERE, "data", "sample_medium.json")
DATA_DEFAULT = DATA_MEDIUM
N_RUNS = 3

def run_baseline(problem, obj, out_dir):
    rows = []
    for run in range(N_RUNS):
        # seed = run supaya tiap run deterministik dan hasilnya bisa diulang
        res = simulated_annealing(problem, obj, seed=run)
        print(f"  [SA run {run}] {summary(res)} stuck={res['extra'].get('stuck_count', '-')}")
        save_json(res, os.path.join(out_dir, f"sa_run{run}.json"))
        plot_objective(res, os.path.join(out_dir, f"sa_run{run}_obj.png"))
        plot_acceptance(res, os.path.join(out_dir, f"sa_run{run}_accept.png"))
        plot_states(problem, res, os.path.join(out_dir, f"sa_run{run}_states.png"))
        rows.append(("Simulated Annealing", run, res["initial_value"],
                     res["final_value"], res["final_valid"],
                     res["iterations"], res["duration_s"]))
    return rows

def run_consistency(problem, obj):
    print(f"{'seed':>4} | {'awal':>8} | {'akhir':>5} | {'valid':>5} | "
          f"{'iter':>5} | {'durasi':>6}")
    print("-" * 48)
    results = []
    for seed in range(10):
        res = simulated_annealing(problem, obj, seed=seed)
        results.append(res['final_value'])
        print(f"{seed:>4} | {res['initial_value']:>8} | {res['final_value']:>5} | "
              f"{str(res['final_valid']):>5} | {res['iterations']:>5} | "
              f"{res['duration_s']:>5.2f}s")

    mean = sum(results) / len(results)
    std = (sum((v - mean) ** 2 for v in results) / len(results)) ** 0.5
    print(f"\nMin: {min(results)}, Max: {max(results)}, "
          f"Mean: {mean:.1f}, Std: {std:.2f}")

def run_alpha(problem, obj):
    print(f"{'alpha':>7} | {'s0':>4} | {'s1':>4} | {'s2':>4} | "
          f"{'max':>4} | {'avg':>5} | {'iter_avg':>8} | {'dur_avg':>7}")
    print("-" * 65)
    for alpha in [0.99, 0.995, 0.999, 0.9999]:
        scores, iters, durs = [], [], []
        for seed in range(3):
            max_it = 200000 if alpha >= 0.9999 else 30000
            res = simulated_annealing(problem, obj, seed=seed,
                                      alpha=alpha, max_iter=max_it)
            scores.append(res['final_value'])
            iters.append(res['iterations'])
            durs.append(res['duration_s'])
        print(f"{alpha:>7} | {scores[0]:>4} | {scores[1]:>4} | {scores[2]:>4} | "
              f"{max(scores):>4} | {sum(scores)/3:>5.1f} | "
              f"{sum(iters)/3:>8.0f} | {sum(durs)/3:>6.2f}s")

def run_t0(problem, obj):
    print(f"{'t0':>6} | {'s0':>4} | {'s1':>4} | {'s2':>4} | "
          f"{'max':>4} | {'avg':>5} | {'dur_avg':>7}")
    print("-" * 55)
    for t0 in [5.0, 10.0, 20.0, 50.0, 100.0]:
        scores, durs = [], []
        for seed in range(3):
            res = simulated_annealing(problem, obj, seed=seed, t0=t0)
            scores.append(res['final_value'])
            durs.append(res['duration_s'])
        print(f"{t0:>6} | {scores[0]:>4} | {scores[1]:>4} | {scores[2]:>4} | "
              f"{max(scores):>4} | {sum(scores)/3:>5.1f} | {sum(durs)/3:>6.2f}s")

def run_scaling():
    print(f"{'dataset':>18} | {'seed':>4} | {'awal':>8} | {'akhir':>5} | "
          f"{'valid':>5} | {'durasi':>6}")
    print("-" * 60)
    for ds in [DATA_SMALL, DATA_MEDIUM]:
        p = load_problem(ds)
        o = Objective(p)
        for seed in range(3):
            res = simulated_annealing(p, o, seed=seed)
            print(f"{os.path.basename(ds):>18} | {seed:>4} | "
                  f"{res['initial_value']:>8} | {res['final_value']:>5} | "
                  f"{str(res['final_valid']):>5} | {res['duration_s']:>5.2f}s")

def main():
    parser = argparse.ArgumentParser(description="Runner SA")
    parser.add_argument("--mode",
                        choices=["baseline", "consistency", "alpha", "t0", "scaling", "all"],
                        default="baseline",
                        help="Jenis eksperimen (default: baseline)")
    parser.add_argument("--dataset", default=DATA_DEFAULT,
                        help="Path dataset JSON (dipakai mode baseline/consistency/alpha/t0)")
    args = parser.parse_args()

    os.makedirs(OUT, exist_ok=True)

    if args.mode in ("baseline", "all"):
        problem = load_problem(args.dataset)
        obj = Objective(problem)
        print(f"\n== BASELINE (dataset={os.path.basename(args.dataset)}) ==")
        d = os.path.join(OUT, "sa")
        os.makedirs(d, exist_ok=True)
        # Baris pertama = header kolom CSV
        rows = [("algoritma", "run", "nilai_awal", "nilai_akhir", "valid",
                 "iterasi", "durasi_s")]
        rows.extend(run_baseline(problem, obj, d))
        csv_path = os.path.join(OUT, "ringkasan.csv")
        with open(csv_path, "w", newline="") as f:
            csv.writer(f).writerows(rows)
        print(f"Ringkasan di {csv_path}")

    if args.mode in ("consistency", "all"):
        problem = load_problem(args.dataset)
        obj = Objective(problem)
        print(f"\n== KONSISTENSI 10 SEED (dataset={os.path.basename(args.dataset)}) ==")
        run_consistency(problem, obj)

    if args.mode in ("alpha", "all"):
        problem = load_problem(args.dataset)
        obj = Objective(problem)
        print(f"\n== PENGARUH ALPHA (dataset={os.path.basename(args.dataset)}) ==")
        run_alpha(problem, obj)

    if args.mode in ("t0", "all"):
        problem = load_problem(args.dataset)
        obj = Objective(problem)
        print(f"\n== PENGARUH SUHU AWAL T0 (dataset={os.path.basename(args.dataset)}) ==")
        run_t0(problem, obj)

    if args.mode in ("scaling", "all"):
        print(f"\n== SKALABILITAS (small vs medium) ==")
        run_scaling()

if __name__ == "__main__":
    main()