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
DATA_DEFAULT = os.path.join(HERE, "data", "sample_medium.json")
N_RUNS = 3

def run_sa(problem, obj, out_dir):
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

def main():
    parser = argparse.ArgumentParser(description="Runner SA")
    parser.add_argument("--dataset", default=DATA_DEFAULT,
                        help="Path dataset JSON")
    args = parser.parse_args()

    problem = load_problem(args.dataset)
    obj = Objective(problem)
    os.makedirs(OUT, exist_ok=True)

    print(f"Dataset   : {args.dataset}")
    print(f"Jumlah run: {N_RUNS}")
    print("-" * 60)

    rows = [("algoritma", "run", "nilai_awal", "nilai_akhir", "valid",
             "iterasi", "durasi_s")]

    print("\n== Simulated Annealing ==")
    d = os.path.join(OUT, "sa")
    os.makedirs(d, exist_ok=True)
    rows.extend(run_sa(problem, obj, d))

    csv_path = os.path.join(OUT, "ringkasan.csv")
    with open(csv_path, "w", newline="") as f:
        csv.writer(f).writerows(rows)

if __name__ == "__main__":
    main()