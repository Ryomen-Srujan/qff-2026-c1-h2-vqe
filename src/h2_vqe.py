import csv
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from scipy.optimize import minimize
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.transpiler import CouplingMap

ROOT = Path(__file__).resolve().parent.parent
PROCESSORS = ROOT / "processors"
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"

TABLES.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

# PROVISIONAL DEVELOPMENT INPUT ONLY.
# Replace with the official QFF C1 Hamiltonian before final submission.
H2 = SparsePauliOp.from_list([
    ("II", -1.052373245772859),
    ("IZ",  0.39793742484318045),
    ("ZI", -0.39793742484318045),
    ("ZZ", -0.01128010425623538),
    ("XX",  0.18093119978423156),
])

REFERENCE_SOURCE = "provisional standard H2 Hamiltonian; not organizer-verified"


def make_ansatz(theta):
    """Two-qubit real/complex variational circuit with two entanglers."""
    qc = QuantumCircuit(2)

    qc.ry(theta[0], 0)
    qc.ry(theta[1], 1)
    qc.rz(theta[2], 0)
    qc.rz(theta[3], 1)

    qc.cx(0, 1)

    qc.ry(theta[4], 0)
    qc.ry(theta[5], 1)
    qc.rz(theta[6], 0)
    qc.rz(theta[7], 1)

    qc.cx(0, 1)
    return qc


def energy(theta):
    state = Statevector.from_instruction(make_ansatz(theta))
    return float(np.real(state.expectation_value(H2)))


def load_processor(filename):
    with (PROCESSORS / filename).open(
        "r", encoding="utf-8-sig"
    ) as f:
        return json.load(f)


def main():
    history = []

    def objective(theta):
        value = energy(theta)
        history.append(value)
        return value

    rng = np.random.default_rng(42)
    initial = rng.uniform(-0.5, 0.5, size=8)

    result = minimize(
        objective,
        initial,
        method="COBYLA",
        options={"maxiter": 500, "rhobeg": 0.5},
    )

    exact_energy = float(np.linalg.eigvalsh(H2.to_matrix()).min())
    optimized_energy = energy(result.x)

    print("=== H2 VQE DEVELOPMENT TEST ===")
    print("Hamiltonian:", REFERENCE_SOURCE)
    print(f"Exact matrix ground energy: {exact_energy:.10f} Ha")
    print(f"VQE energy:                 {optimized_energy:.10f} Ha")
    print(f"Absolute energy error:      {abs(optimized_energy-exact_energy):.10f} Ha")
    print(f"Optimizer success flag:     {result.success}")
    print(f"Objective evaluations:      {len(history)}")

    with (TABLES / "h2_convergence.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.writer(f)
        writer.writerow(["evaluation", "energy_hartree"])
        writer.writerows(enumerate(history, start=1))

    plt.figure()
    plt.plot(range(1, len(history) + 1), history)
    plt.axhline(exact_energy, linestyle="--", label="Exact matrix ground energy")
    plt.xlabel("Objective evaluation")
    plt.ylabel("Energy (Hartree)")
    plt.title("H2 VQE convergence — provisional development test")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "h2_vqe_convergence.png", dpi=160)
    plt.close()

    logical_circuit = make_ansatz(result.x)
    architecture_rows = []

    for filename in ["processor_A.json", "processor_B.json"]:
        config = load_processor(filename)

        directed_edges = []
        for a, b in config["coupling_map"]:
            directed_edges.extend([(a, b), (b, a)])

        coupling = CouplingMap(couplinglist=directed_edges)

        compiled = transpile(
            logical_circuit,
            coupling_map=coupling,
            basis_gates=["rz", "sx", "x", "cx"],
            optimization_level=1,
            seed_transpiler=42,
        )

        ops = compiled.count_ops()
        row = {
            "processor": config["name"],
            "physical_qubits": config["num_qubits"],
            "logical_qubits": logical_circuit.num_qubits,
            "depth": compiled.depth(),
            "total_gates": sum(ops.values()),
            "cx_count": ops.get("cx", 0),
            "explicit_swap_count": ops.get("swap", 0),
            "ideal_vqe_energy_hartree": optimized_energy,
            "energy_error_hartree": abs(optimized_energy - exact_energy),
            "noise_model": "not applied",
            "status": "provisional development test",
        }
        architecture_rows.append(row)

        output = FIGURES / (
            filename.replace(".json", "_h2_circuit.txt")
        )
        output.write_text(
            str(compiled.draw(output="text")), encoding="utf-8"
        )

        print(f"\n{config['name']}:")
        for key, value in row.items():
            print(f"  {key}: {value}")

    with (TABLES / "h2_architecture_metrics.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=architecture_rows[0].keys()
        )
        writer.writeheader()
        writer.writerows(architecture_rows)

    print("\nSaved:")
    print("  results/tables/h2_convergence.csv")
    print("  results/tables/h2_architecture_metrics.csv")
    print("  results/figures/h2_vqe_convergence.png")
    print("\nIMPORTANT: provisional ideal-simulation results only.")
    print("Official inputs and noise settings must be verified before submission.")


if __name__ == "__main__":
    main()
