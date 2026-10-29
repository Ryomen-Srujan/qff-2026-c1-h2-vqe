
"""Four-qubit H2 VQE using the reconstructed notebook Hamiltonian.

The Hamiltonian coefficients are rounded values recovered from the saved
main.ipynb output; they have not been independently verified as organizer-issued.
"""
import csv
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "h2_hamiltonian.json"
TABLES = ROOT / "results" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)


def load_hamiltonian():
    with DATA.open(encoding="utf-8-sig") as f:
        data = json.load(f)
    operator = SparsePauliOp.from_list(
        [(pauli, float(coefficient))
         for pauli, coefficient in data["pauli_terms"]]
    )
    return operator, data


def make_ansatz(theta):
    """Four-qubit hardware-efficient ansatz with two entangling layers."""
    qc = QuantumCircuit(4)
    for q in range(4):
        qc.ry(theta[q], q)
        qc.rz(theta[4 + q], q)

    for q in range(3):
        qc.cx(q, q + 1)

    for q in range(4):
        qc.ry(theta[8 + q], q)
        qc.rz(theta[12 + q], q)

    for q in range(3):
        qc.cx(q, q + 1)

    return qc


def energy(theta, hamiltonian):
    state = Statevector.from_instruction(make_ansatz(theta))
    return float(np.real(state.expectation_value(hamiltonian)))


def main():
    hamiltonian, metadata = load_hamiltonian()
    exact_energy = float(np.linalg.eigvalsh(hamiltonian.to_matrix())[0])
    history = []

    def objective(theta):
        value = energy(theta, hamiltonian)
        history.append(value)
        return value

    rng = np.random.default_rng(42)
    initial = rng.uniform(-0.5, 0.5, size=16)

    result = minimize(
        objective,
        initial,
        method="COBYLA",
        options={"maxiter": 2000, "rhobeg": 0.5},
    )

    vqe_energy = energy(result.x, hamiltonian)
    error_ha = abs(vqe_energy - exact_energy)

    print("=== FOUR-QUBIT H2 VQE ===")
    print("Hamiltonian source:", metadata["source"])
    print("Qubits:", hamiltonian.num_qubits)
    print("Pauli terms:", len(hamiltonian))
    print(f"Exact matrix energy: {exact_energy:.10f} Ha")
    print(f"VQE energy:         {vqe_energy:.10f} Ha")
    print(f"Absolute error:     {error_ha:.10f} Ha")
    print(f"Absolute error:     {error_ha * 1000:.6f} mHa")
    print(f"Chemical accuracy:  {error_ha < 0.0016}")
    print("Optimizer success:", result.success)
    print("Optimizer message:", result.message)
    print("Objective evaluations:", result.nfev)

    with (TABLES / "h2_four_qubit_convergence.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.writer(f)
        writer.writerow(["evaluation", "energy_hartree"])
        writer.writerows(enumerate(history, start=1))

    print("Saved results/tables/h2_four_qubit_convergence.csv")


if __name__ == "__main__":
    main()
