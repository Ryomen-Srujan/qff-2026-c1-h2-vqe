import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from qiskit import transpile
from qiskit.circuit.library import efficient_su2
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator
from qiskit_aer.primitives import Estimator as AerEstimator
from src.processors import load_coupling_map, build_noise_model

# Load saved 4-qubit H2 Hamiltonian (no PySCF required).
data = json.loads(
    Path("data/h2_hamiltonian.json").read_text(encoding="utf-8-sig")
)
hamiltonian = SparsePauliOp.from_list(
    [(term, float(coef)) for term, coef in data["pauli_terms"]]
)
exact_energy = float(np.linalg.eigvalsh(hamiltonian.to_matrix())[0])
print(f"Exact electronic energy: {exact_energy:.10f} Ha")

# Use the same 16-parameter ansatz as the verified four-qubit VQE.
from qiskit import QuantumCircuit

def make_ansatz():
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

# Build a parameterized circuit using 16 symbolic parameters.
from qiskit.circuit import ParameterVector
theta = ParameterVector("theta", 16)
ansatz = make_ansatz()
rng = np.random.default_rng(42)
x0 = rng.uniform(-0.5, 0.5, size=16)

def cost(params, circuit, operator, estimator):
    bound = circuit.assign_parameters(params)
    try:
        job = estimator.run([(bound, operator)])
        result = job.result()
        return float(np.real(result[0].data.evs))
    except (TypeError, ValueError, AttributeError, KeyError, IndexError):
        job = estimator.run([bound], [operator])
        result = job.result()
        if hasattr(result, "values"):
            return float(np.real(result.values[0]))
        return float(np.real(result[0].data.evs))

print("Optimizing ideal starting parameters...")
ideal = minimize(
    cost, x0, args=(ansatz, hamiltonian, StatevectorEstimator()),
    method="COBYLA", options={"maxiter": 1200, "tol": 1e-7}
)
print(f"Ideal VQE energy: {ideal.fun:.8f} Ha")
print(f"Ideal error: {abs(ideal.fun-exact_energy)*1000:.4f} mHa")

noise = build_noise_model(0.001, 0.005, 0.01)
rows = []

for name, path in [
    ("Processor_A", "processors/processor_a.json"),
    ("Processor_B", "processors/processor_b.json"),
]:
    cmap, cfg = load_coupling_map(path)
    circuit = transpile(
        ansatz,
        coupling_map=cmap,
        basis_gates=["rz", "sx", "x", "cx"],
        optimization_level=1,
        layout_method="sabre",
        routing_method="sabre",
        seed_transpiler=42,
    )
    operator = hamiltonian.apply_layout(circuit.layout)

    print(f"\n{name}: {cfg['num_qubits']} physical qubits")
    print(f"Depth={circuit.depth()}, CX={circuit.count_ops().get('cx', 0)}")
    print(f"Running noisy VQE (up to 60 optimizer evaluations)...")

    estimator = AerEstimator(
        backend_options={"method": "density_matrix", "noise_model": noise},
        run_options={"shots": 4096, "seed": 42},
    )
    result = minimize(
        cost, ideal.x, args=(circuit, operator, estimator),
        method="COBYLA", options={"maxiter": 60, "tol": 1e-5}
    )

    error = abs(result.fun - exact_energy) * 1000
    print(f"Noisy energy: {result.fun:.8f} Ha")
    print(f"Absolute error: {error:.4f} mHa")

    rows.append({
        "Processor": name,
        "Physical_Qubits": cfg["num_qubits"],
        "Logical_Qubits": 4,
        "Energy_Ha": result.fun,
        "Exact_Electronic_Energy_Ha": exact_energy,
        "Error_mHa": error,
        "Chemical_Accuracy_1_6mHa": error <= 1.6,
        "Depth": circuit.depth(),
        "CX": circuit.count_ops().get("cx", 0),
        "Explicit_SWAP": circuit.count_ops().get("swap", 0),
        "Shots": 4096,
        "Optimizer_Evaluations": result.nfev,
        "Noise_1Q": 0.001,
        "Noise_CX": 0.005,
        "Readout_Bitflip": 0.01,
    })

out = Path("results/tables/h2_noisy_ab_final.csv")
out.parent.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(out, index=False)
print("\nSaved:", out)
print(pd.DataFrame(rows).to_string(index=False))
