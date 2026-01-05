from __future__ import annotations

from typing import Optional

import matplotlib.pyplot as plt

from .core import PVLoopPoints


def plot_pv_loop(points: PVLoopPoints, *, title: Optional[str] = None, output_path: Optional[str] = None) -> None:
    """
    Plota ESPVR e loop PV.
    Se output_path for fornecido, salva em arquivo. Caso contrário, exibe (plt.show()).
    """
    # ESPVR
    (v0, p0), (ves, pes) = points.espvr
    loop_v = [v for v, _ in points.loop]
    loop_p = [p for _, p in points.loop]

    plt.figure()
    plt.plot([v0, ves], [p0, pes], marker="o", label="ESPVR")
    plt.plot(loop_v, loop_p, marker="o", label="Loop PV")
    plt.xlabel("Volume (mL)")
    plt.ylabel("Pressão (mmHg)")
    if title:
        plt.title(title)
    plt.legend()
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=200)
        plt.close()
    else:
        plt.show()
