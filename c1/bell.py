"""Objective 1: Bell test on Processor D -> bell.csv (2 pairs x ideal/noisy)."""
import os
import pandas as pd
from c1.setup import ROOT, get_processor_D
from qff_chem import bell_experiment, coupling_map_from_edges


def d_pairs(pD):
    """(adjacent pair, farthest pair) of physical qubits in D."""
    cm = coupling_map_from_edges(pD["edges"], pD["num_qubits"])
    n = pD["num_qubits"]
    pairs = [(a, b) for a in range(n) for b in range(a + 1, n)]
    near = next(p for p in pairs if cm.distance(*p) == 1)
    far = max(pairs, key=lambda p: (cm.distance(*p), -p[0]))
    return near, far


def run_bell():
    pD = get_processor_D()
    rows = []
    for pair in d_pairs(pD):
        for noisy in (False, True):
            r = bell_experiment(pD, pair, noisy)
            rows.append({"pair": f"{pair[0]}-{pair[1]}", "pair_distance": r["pair_distance"],
                         "condition": "noisy" if noisy else "ideal", "two_qubit_gates": r["cx"],
                         **{k: r[k] for k in ("XX", "XX_se", "YY", "YY_se", "ZZ", "ZZ_se", "fidelity", "fidelity_se")}})
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(ROOT, "results", "tables", "bell.csv"), index=False)
    return df
