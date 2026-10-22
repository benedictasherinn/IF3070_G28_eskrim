import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import textwrap

def plot_history(result, path=None):
    """plot objective function vs iterations"""
    history = result["history"]
    iterations = range(len(history))

    fig = plt.figure()
    marker = "o" if len(history) <= 50 else None    #titik cuma kalau datanya sedikit
    plt.plot(iterations, history, marker=marker, label="Objective")

    plt.xlabel("Iteration")
    plt.ylabel("Objective Value")
    plt.title(
        f"{result['algorithm']}: "
        f"Iterations={result['iterations']}\n"
        f"Durasi pencarian={result['duration_s']} detik",
    )
    plt.legend()

    if path:
        plt.savefig(path, dpi=120)
        plt.close()

    return fig


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
    cells_of = {}

    for vid in problem.ids:
        pl = placements.get(vid)
        if pl is None:
            continue

        x, y, ori = pl
        c, r = problem.by[vid].footprint(ori)
        cells_of[vid] = [(x + dx, y + dy) for dy in range(r) for dx in range(c)]
        for cell in cells_of[vid]:
            occupancy[cell] = occupancy.get(cell, 0) + 1

        ax.add_patch(Rectangle(
            (x, y), c, r,
            facecolor=vehicle_color,
            edgecolor="black",
            linewidth=0.8
        ))

    #red=overlap
    for (cx, cy), count in occupancy.items():
        if count > 1:
            ax.add_patch(Rectangle(
                (cx, cy), 1, 1,
                facecolor="red",
                edgecolor="red",
                alpha=0.55,
                hatch="///"
            ))

    #kendaraan yang bertumpuk ditandai nomor biar namanya gak tabrakan
    numbers = {vid: i + 1 for i, vid in enumerate(problem.ids)}
    stacked = [vid for vid, cells in cells_of.items() if any(occupancy[cell] > 1 for cell in cells)]
    used = set()
    for vid, cells in cells_of.items():
        x, y, ori = placements[vid]
        c, r = problem.by[vid].footprint(ori)
        if vid not in stacked:
            ax.text(
                x + c / 2, y + r / 2, vid,
                ha="center", va="center", fontsize=8
            )
            continue
        inside = [cl for cl in cells if 0 <= cl[0] < sh.cols and 0 <= cl[1] < sh.rows] or cells
        cell = next((cl for cl in inside if cl not in used), inside[0])
        used.add(cell)
        ax.text(
            cell[0] + 0.5, cell[1] + 0.5, str(numbers[vid]),
            ha="center", va="center", fontsize=7, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="black", linewidth=0.5)
        )

    outside = [
        vid for vid in problem.ids
        if placements.get(vid) is None
    ]

    label = ", ".join(outside) if outside else "-"
    lines = [textwrap.fill(f"Di luar kapal: {label}", width=38, break_on_hyphens=False)]
    if stacked:
        stacked_label = ", ".join(f"{numbers[vid]}={vid}" for vid in stacked)
        lines.append(textwrap.fill(f"Bertumpuk: {stacked_label}", width=38, break_on_hyphens=False))
    ax.set_xlabel("\n".join(lines), fontsize=7)
    ax.set_title(title, fontsize=9)


def plot_states(problem, result, path=None):
    """Menggambar perbandingan state awal dan state akhir pada kapal"""
    sh = problem.ship
    pw = max(3.5, sh.cols * 0.5)
    ph = max(3.5, sh.rows * 0.4)

    fig, axes = plt.subplots(1, 2, figsize=(2 * pw + 1, ph + 1.8))

    t_init = f"State awal\nObjective = {result['initial_value']}"
    t_final = f"State akhir\nObjective = {result['final_value']}"

    draw_state(problem, result["initial_placements"], axes[0], t_init)
    draw_state(problem, result["final_placements"], axes[1], t_final)

    suptitle = f"{result['algorithm']} | iterasi={result['iterations']}"
    if "best_restart" in result["extra"]:    #random restart: state akhir dari pendakian terbaik
        suptitle += f" | state akhir dari pendakian ke-{result['extra']['best_restart'] + 1}"
    fig.suptitle(suptitle, fontsize=11)

    plt.tight_layout()
    if path:
        fig.savefig(path, dpi=120)
        plt.close(fig)
    else:
        plt.show()
    return fig


def print_result(result, label=None):
    """Mencetak hasil Hill-climbing"""
    print("=" * 60)
    print(label or result["algorithm"])
    print("=" * 60)
    print("\n=== STATE AWAL ===")
    print(result["initial_render"])
    print(f"Objective awal  : {result['initial_value']}")
    print("\n=== STATE AKHIR ===")
    print(result["final_render"])
    print(f"Objective akhir : {result['final_value']}")
    print(f"Valid           : {'Ya' if result['final_valid'] else 'TIDAK'}")
    print(f"Banyak iterasi  : {result['iterations']}")
    print(f"Durasi pencarian: {result['duration_s']} detik\n")
