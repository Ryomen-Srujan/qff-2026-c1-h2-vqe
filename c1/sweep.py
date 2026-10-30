"""PS-C1 depth x optimizer x seed sweep (official settings) -> results/tables/c1_sweep.csv."""
import json, os
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from c1.setup import (ROOT, OPERATORS, E_FCI, MAIN_LABEL, get_processor_D, hf_circuit)
from qff_chem import (hardware_efficient_ansatz, energy_statevector, CountedCost,
                      spsa_minimize, circuit_metrics)

OPTIMIZERS = ("COBYLA", "SPSA")
SEEDS = (0, 1, 2)


def run_single(label, depth, optimizer, seed, processor_D, cobyla_iters=200, spsa_iters=300):
    op, const, hf, _ = OPERATORS[label]
    ansatz, params = hardware_efficient_ansatz(op.num_qubits, depth, hf_circuit(hf))
    x0 = np.random.default_rng(seed).uniform(-np.pi, np.pi, len(params))
    bind = lambda x: ansatz.assign_parameters(dict(zip(params, x)))        # noqa: E731
    cost = CountedCost(lambda x: energy_statevector(bind(x), op, const))
    if optimizer == "COBYLA":
        res = minimize(cost, x0, method="COBYLA", options={"maxiter": cobyla_iters})
        energy, theta = float(res.fun), res.x
    else:
        out = spsa_minimize(cost, x0, maxiter=spsa_iters, seed=seed)
        energy, theta = float(out["fun"]), out["x"]
    m = circuit_metrics(bind(theta), processor_D)
    row = {"operator": label, "ansatz": "hardware_efficient", "depth": depth, "optimizer": optimizer,
           "seed": seed, "energy": energy, "error_mha": (energy - E_FCI) * 1e3,
           "optimizer_calls": cost.calls, "cx_on_D": m["cx"], "depth_on_D": m["depth"]}
    return row, list(cost.history), [float(t) for t in theta]


def run_sweep(label=MAIN_LABEL, depths=(1, 2), tag="c1_sweep"):
    """Returns (DataFrame, histories{(depth,opt,seed)}, thetas{...}). Writes results/tables/<tag>.csv."""
    pD = get_processor_D()
    rows, hist, thetas = [], {}, {}
    for d in depths:
        for opt in OPTIMIZERS:
            for s in SEEDS:
                r, h, th = run_single(label, d, opt, s, pD)
                rows.append(r); hist[(d, opt, s)] = h; thetas[(d, opt, s)] = th
    df = pd.DataFrame(rows)
    os.makedirs(os.path.join(ROOT, "results", "tables"), exist_ok=True)
    df.to_csv(os.path.join(ROOT, "results", "tables", f"{tag}.csv"), index=False)
    return df, hist, thetas


def best_run(df, thetas, label=MAIN_LABEL, path="results/best_run_c1.json"):
    """Best = smallest |error|; ties (within 1e-9 mHa) -> fewest optimizer calls. Saves the parameters."""
    d = df.assign(a=df.error_mha.abs().round(6)).sort_values(["a", "optimizer_calls"]).iloc[0]
    key = (int(d.depth), d.optimizer, int(d.seed))
    out = {"operator": label, "depth": key[0], "optimizer": key[1], "seed": key[2],
           "error_mha": float(d.error_mha), "energy": float(d.energy), "theta": thetas[key]}
    with open(os.path.join(ROOT, path), "w") as f:
        json.dump(out, f, indent=2)
    return out


def plot_best_convergence(df, hist, tag="c1_convergence", title=""):
    """Convergence (error vs optimizer calls) of the best seed of each depth x optimizer combination."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for (d, opt), sub in df.groupby(["depth", "optimizer"]):
        s = int(sub.loc[sub.error_mha.abs().idxmin(), "seed"])
        h = np.array(hist[(d, opt, s)])
        ax.plot(np.arange(1, len(h) + 1), np.abs(h - E_FCI) * 1e3 + 1e-9,
                label=f"depth {d}, {opt} (seed {s})")
    ax.axhline(1.6, ls="--", c="gray", lw=0.8, label="chemical accuracy 1.6 mHa")
    ax.set_yscale("log"); ax.set_xlabel("optimizer calls (SPSA incl. calibration)")
    ax.set_ylabel("|E - E_FCI| (mHa)"); ax.set_title(title); ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(ROOT, "results", "figures", f"{tag}.png"), dpi=200)
    return fig
