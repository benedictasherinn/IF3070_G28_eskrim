import argparse
import csv
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import load_problem, Objective, summary, save_json
from algorithms.simulated_annealing import simulated_annealing
from algorithms.plots_sa import plot_objective, plot_acceptance, plot_states as plot_states_sa
from algorithms.geneticAlgorithm import GeneticAlgorithm
from algorithms.plotGenetic import plot_history, plot_states as plot_states_ga

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "output")
DATA_SMALL = os.path.join(HERE, "data", "sample_small.json")
DATA_MEDIUM = os.path.join(HERE, "data", "sample_medium.json")
DATA_DEFAULT = DATA_MEDIUM
N_RUNS = 3

CSV_HEADER = ("algoritma", "run", "nilai_awal", "nilai_akhir", "valid", "iterasi", "durasi_s")

#Variabel Genetic Algorithm
CONTROL_POPULATION = 50
CONTROL_ITERATION = 150
POPULATIONS = [20, 50, 100]
ITERATIONS = [50, 100, 200]

#SIMULATED ANNEALING
def run_sa(problem, obj, out_dir):
    rows = []
    for run in range(N_RUNS):
        # seed = run supaya tiap run deterministik dan hasilnya bisa diulang
        res = simulated_annealing(problem, obj, seed=run)
        print(f"  [SA run {run}] {summary(res)} stuck={res['extra'].get('stuck_count', '-')}")
        save_json(res, os.path.join(out_dir, f"sa_run{run}.json"))
        plot_objective(res, os.path.join(out_dir, f"sa_run{run}_obj.png"))
        plot_acceptance(res, os.path.join(out_dir, f"sa_run{run}_accept.png"))
        plot_states_sa(problem, res, os.path.join(out_dir, f"sa_run{run}_states.png"))
        rows.append(("Simulated Annealing", run, res["initial_value"],
                     res["final_value"], res["final_valid"],
                     res["iterations"], res["duration_s"]))
    return rows

def run_sa_consistency(problem, obj):
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

def run_sa_alpha(problem, obj):
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

def run_sa_t0(problem, obj):
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

def run_sa_scaling():
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

#GENETIC ALGORITHM
def run_ga(problem, out_dir):
    """Menjalankan Genetic Algorithm"""
    #Kelompok A: Jumlah populasi sebagai kontrol, iterasi bervariasi
    kelA = [(CONTROL_POPULATION, iteration) for iteration in ITERATIONS]

    #Kelompok B: Jumlah iterasi tetap, populasi bervariasi
    kelB = [(population, CONTROL_ITERATION) for population in POPULATIONS]

    all_results = {}
    for population, iteration in dict.fromkeys(kelA + kelB):
        print(f"\n---- GA populasi={population}, iterasi={iteration} ----")
        folder = os.path.join(out_dir, f"populasi{population}_iterasi{iteration}")
        os.makedirs(folder, exist_ok=True)
        results = []

        for run in range(N_RUNS):
            result = GeneticAlgorithm(problem, population, iteration, run).run()
            results.append(result)
            print(f"  run {run}: objective akhir={result['final_value']} "
                  f"({'valid' if result['final_valid'] else 'Tidak valid'}) | "
                  f"populasi={population} | iterasi={iteration} | durasi={result['duration_s']} detik")

            base = os.path.join(folder, f"run{run}")
            save_json(result, base + ".json")
            plot_states_ga(problem, result, base + "_states.png")
            fig = plot_history(result)
            extra = result["extra"]
            if min(extra["max_history"] + extra["average_history"]) < -1000:
                fig.axes[0].set_yscale("symlog", linthresh=100)
            fig.savefig(base + "_history.png", dpi=120)
            plt.close(fig)

        all_results[(population, iteration)] = results

    rows = []
    for (population, iteration), results in all_results.items():
        for run, result in enumerate(results):
            rows.append((f"Genetic Algorithm (pop={population}, it={iteration})", run, result["initial_value"],
                         result["final_value"], result["final_valid"], result["iterations"], result["duration_s"]))
    invalid = [f"{r[0]} run {r[1]}" for r in rows if not r[4]]
    if invalid:
        print("\nHasil akhir Tidak valid pada:", ", ".join(invalid))
    return rows

#MAIN
def main():
    parser = argparse.ArgumentParser(description="Runner algoritma local search")
    parser.add_argument("--algo", nargs="+", choices=["sa", "ga"], default=["sa", "ga"],
                        help="algoritma yang dijalankan (default: semua)")
    parser.add_argument("--dataset", default=DATA_DEFAULT, help="Path dataset JSON")
    parser.add_argument("--extra", nargs="+", choices=["consistency", "alpha", "scaling"], default=[],
                        help="eksperimen tambahan SA (opsional)")
    args = parser.parse_args()

    problem = load_problem(args.dataset)
    obj = Objective(problem)
    os.makedirs(OUT, exist_ok=True)

    print(f"Dataset   : {args.dataset}")
    print(f"Algoritma : {', '.join(args.algo)}")
    print(f"Jumlah run: {N_RUNS}")
    print("-" * 60)

    rows = [CSV_HEADER]

    if "sa" in args.algo:
        print("\n==== Simulated Annealing ====")
        d = os.path.join(OUT, "sa")
        os.makedirs(d, exist_ok=True)
        rows.extend(run_sa(problem, obj, d))

    if "ga" in args.algo:
        print("\n==== Genetic Algorithm ====")
        d = os.path.join(OUT, "ga")
        os.makedirs(d, exist_ok=True)
        rows.extend(run_ga(problem, d))

    csv_path = os.path.join(OUT, "ringkasan.csv")
    with open(csv_path, "w", newline="") as f:
        csv.writer(f).writerows(rows)
    print(f"\nRingkasan di {csv_path}")

    if "consistency" in args.extra:
        print(f"\n==== SA: Konsistensi 10 Seed (dataset={os.path.basename(args.dataset)}) ====")
        run_sa_consistency(problem, obj)
    if "alpha" in args.extra:
        print(f"\n==== SA: Pengaruh Alpha (dataset={os.path.basename(args.dataset)}) ====")
        run_sa_alpha(problem, obj)
    if "scaling" in args.extra:
        print("\n==== SA: Skalabilitas (small vs medium) ====")
        run_sa_scaling()

if __name__ == "__main__":
    main()