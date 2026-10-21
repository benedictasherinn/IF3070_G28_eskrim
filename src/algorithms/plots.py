import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_objective(res, path):
    """Plot nilai objective function vs iterasi"""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(res["history"], linewidth=1)
    ax.set_title(f"{res['algorithm']}: Objective vs Iterasi")
    ax.set_xlabel("Iterasi")
    ax.set_ylabel("Nilai Objective")
    ax.grid(True, linewidth=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_acceptance(res, path):
    """Plot peluang penerimaan e^(dE/T) vs iterasi"""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(res["extra"].get("acceptance_probs", []), linewidth=0.8)
    ax.set_title("Simulated Annealing: e^(dE/T) vs Iterasi")
    ax.set_xlabel("Iterasi")
    ax.set_ylabel("Peluang Penerimaan")
    ax.grid(True, linewidth=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)