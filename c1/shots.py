"""PS-C1 shot study: 1,024 / 8,192 shots per group x {ideal, noisy on D} -> c1_shots.csv (4 rows)."""
import os
import numpy as np
import pandas as pd
from c1.setup import ROOT, OPERATORS, E_FCI, get_processor_D, hf_circuit
from qff_chem import hardware_efficient_ansatz, energy_shots, SHOT_SETTINGS, CHEMICAL_ACCURACY


def bound_best_circuit(best):
    op, const, hf, _ = OPERATORS[best["operator"]]
    ansatz, params = hardware_efficient_ansatz(op.num_qubits, best["depth"], hf_circuit(hf))
    return ansatz.assign_parameters(dict(zip(params, best["theta"]))), op, const


def run_shot_study(best):
    qc, op, const = bound_best_circuit(best)
    pD = get_processor_D()
    rows = []
    for noisy in (False, True):
        for S in SHOT_SETTINGS:
            r = energy_shots(qc, op, const, shots_per_group=S, noisy=noisy, processor=pD if noisy else None)
            err = (r["energy"] - E_FCI) * 1e3
            rows.append({"shots_per_group": S, "condition": "noisy_D" if noisy else "ideal",
                         "energy": r["energy"], "std_error": r["std_error"], "error_mha": err,
                         "groups": r["groups"], "total_shots": r["total_shots"],
                         # chemical accuracy "within SE": |error| - SE <= 1.6 mHa
                         "within_chem_acc_1se": abs(err) - r["std_error"] * 1e3 <= CHEMICAL_ACCURACY * 1e3,
                         "within_chem_acc_point": abs(err) <= CHEMICAL_ACCURACY * 1e3})
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(ROOT, "results", "tables", "c1_shots.csv"), index=False)
    return df
