import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import textwrap


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


def draw_state(problem, placements, ax, title):
    """Menggambar posisi kendaraan dan overlap pada kapal"""
    sh = problem.ship
    vehicle_color = "#D9E2F3"

    ax.set_xlim(0, sh.cols)
    ax.set_ylim(sh.rows, 0)
    ax.set_aspect("equal")
    ax.set_xticks(range(sh.cols + 1))
    ax.set_yticks(range(sh.rows + 1))
    ax.tick_params(labelsize=6)
    ax.grid(True, color="#cccccc", linewidth=0.5)

    occupancy = {}

    for vid in problem.ids:
        pl = placements.get(vid)
        if pl is None:
            continue

        x, y, ori = pl
        c, r = problem.by[vid].footprint(ori)

        ax.add_patch(Rectangle(
            (x, y), c, r,
            facecolor=vehicle_color,
            edgecolor="black",
            linewidth=0.8
        ))

        ax.text(
            x + c / 2, y + r / 2, vid,
            ha="center", va="center", fontsize=8
        )

        for dx in range(c):
            for dy in range(r):
                cell = (x + dx, y + dy)
                occupancy[cell] = occupancy.get(cell, 0) + 1

    # Tandai sel overlap dengan warna merah
    for (cx, cy), count in occupancy.items():
        if count > 1:
            ax.add_patch(Rectangle(
                (cx, cy), 1, 1,
                facecolor="red",
                edgecolor="red",
                alpha=0.55,
                hatch="///"
            ))

    outside = [vid for vid in problem.ids if placements.get(vid) is None]
    label = ", ".join(outside) if outside else "-"
    ax.set_xlabel(
        textwrap.fill(f"Di luar kapal: {label}", width=38),
        fontsize=7
    )
    ax.set_title(title, fontsize=9)


def plot_states(problem, res, path):
    """Menggambar perbandingan state awal dan state akhir pada kapal"""
    sh = problem.ship
    pw = max(3.5, sh.cols * 0.5)
    ph = max(3.5, sh.rows * 0.4)

    fig, axes = plt.subplots(1, 2, figsize=(2 * pw + 1, ph + 1.8))

    t_init = f"State awal\nObjective = {res['initial_value']}"
    t_final = f"State akhir\nObjective = {res['final_value']}"

    draw_state(problem, res["initial_placements"], axes[0], t_init)
    draw_state(problem, res["final_placements"], axes[1], t_final)

    fig.suptitle(
        f"{res['algorithm']} | iterasi={res['iterations']} | durasi={res['duration_s']}s",
        fontsize=11
    )

    plt.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)