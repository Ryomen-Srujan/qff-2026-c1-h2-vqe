"""PS-C1 resources.csv (JW and reduced circuits x A/B/D) and c1_mapping.csv."""
import os
import pandas as pd
from c1.setup import ROOT, OPERATORS, E_FCI, get_processor_D, hf_circuit, pauli_cost, exact_ground_energy, PROCESSOR_A, PROCESSOR_B
from qff_chem import hardware_efficient_ansatz, circuit_metrics


def _bound(label, depth, theta=None):
    op, const, hf, _ = OPERATORS[label]
    qc, params = hardware_efficient_ansatz(op.num_qubits, depth, hf_circuit(hf))
    vals = theta if theta is not None else [0.1 * (i + 1) for i in range(len(params))]   # structure only
    return qc.assign_parameters(dict(zip(params, vals)))


def resources_table(depths=(1, 2)):
    procs = {"A": PROCESSOR_A, "B": PROCESSOR_B, "D": get_processor_D()}
    rows = []
    for label in OPERATORS:
        for d in depths:
            qc = _bound(label, d)
            for pname, p in procs.items():
                m = circuit_metrics(qc, p)
                row = {"ps": "C1", "circuit_label": f"{label}-HEA-depth{d}", "processor": pname,
                       "executable": m["executable"]}
                if m["executable"]:
                    row.update({k: m[k] for k in ("logical_qubits", "physical_qubits", "logical_cx", "cx",
                                                  "depth", "two_q_depth", "swaps", "cx_overhead")})
                else:
                    row["note"] = f"not executable: {m['reason']}"
                rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(ROOT, "results", "tables", "resources.csv"), index=False)
    return df


def mapping_table(depth=1):
    pD = get_processor_D()
    rows = []
    for label, (op, const, hf, method) in OPERATORS.items():
        pc = pauli_cost(op)
        m = circuit_metrics(_bound(label, depth), pD)
        rows.append({"operator_label": label, "method": method, "qubits": pc["qubits"],
                     "pauli_terms": pc["pauli_terms"], "qwc_groups": pc["qwc_groups"],
                     "exact_energy": exact_ground_energy(op, const), "cx_on_D": m["cx"]})
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(ROOT, "results", "tables", "c1_mapping.csv"), index=False)
    return df
