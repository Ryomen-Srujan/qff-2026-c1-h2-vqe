import csv
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, "starter")
import qff_chem as qc

from qiskit_nature.second_q.operators import ElectronicIntegrals
from qiskit_nature.second_q.hamiltonians import ElectronicEnergy
from qiskit_nature.second_q.mappers import ParityMapper
from qiskit_nature.second_q.circuit.library import HartreeFock


# Official C1 reference
REFERENCE_ENERGY = -1.1373060357534004
MAXITER = 300

# Load chemistry integrals
data = np.load("data/c1/h2_0.735_integrals.npz")
integrals = ElectronicIntegrals.from_raw_integrals(
    data["h1"], data["h2_chemist"]
)
fermionic_operator = ElectronicEnergy(integrals).second_q_op()

# Reduce from 4 qubits to 2 using parity mapping
mapper = ParityMapper(
    num_particles=(int(data["n_alpha"]), int(data["n_beta"]))
)
operator = mapper.map(fermionic_operator)
constant = float(data["e_core"])

# Construct the correct 2-qubit Hartree-Fock state
hf = HartreeFock(2, (1, 1), mapper)

# Load our validated Processor D
processor = qc.load_processor("processors/processor_D.json")

print("Reduced qubits:", operator.num_qubits)
print("Exact energy:", qc.exact_ground_energy(operator, constant))
print("Starting VQE sweep...\n")

Path("results/tables").mkdir(parents=True, exist_ok=True)

sweep_rows = []
history_rows = []

for reps in [1, 2]:
    circuit, parameters = qc.hardware_efficient_ansatz(
        n_qubits=2,
        reps=reps,
        initial=hf
    )

    for optimizer_name in ["COBYLA", "SPSA"]:
        for seed in [0, 1, 2]:

            rng = np.random.default_rng(seed)
            x0 = rng.uniform(-np.pi, np.pi, len(parameters))

            def energy_function(values):
                bound = circuit.assign_parameters(
                    dict(zip(parameters, values))
                )
                return qc.energy_statevector(
                    bound, operator, constant
                )

            cost = qc.CountedCost(energy_function)

            if optimizer_name == "COBYLA":
                result = minimize(
                    cost,
                    x0,
                    method="COBYLA",
                    options={"maxiter": MAXITER, "rhobeg": 0.5, "tol": 1e-6}
                )
                best_parameters = result.x
                final_energy = float(result.fun)

            else:
                result = qc.spsa_minimize(
                    cost,
                    x0,
                    maxiter=MAXITER,
                    seed=seed
                )
                best_parameters = result["x"]
                final_energy = float(result["fun"])

            # Evaluate the final optimized circuit on Processor D
            final_circuit = circuit.assign_parameters(
                dict(zip(parameters, best_parameters))
            )
            metrics = qc.circuit_metrics(final_circuit, processor)

            error_mha = abs(final_energy - REFERENCE_ENERGY) * 1000

            sweep_rows.append({
                "ansatz": "hardware_efficient",
                "depth": reps,
                "optimizer": optimizer_name,
                "seed": seed,
                "energy": final_energy,
                "error_mha": error_mha,
                "optimizer_calls": cost.calls,
                "cx_on_D": metrics["cx"],
                "depth_on_D": metrics["depth"]
            })

            for evaluation, energy in enumerate(cost.history, start=1):
                history_rows.append({
                    "ansatz_depth": reps,
                    "optimizer": optimizer_name,
                    "seed": seed,
                    "evaluation": evaluation,
                    "energy": energy
                })

            print(
                f"Depth={reps}, Optimizer={optimizer_name}, Seed={seed}: "
                f"Energy={final_energy:.10f} Ha, "
                f"Error={error_mha:.4f} mHa, "
                f"Calls={cost.calls}, "
                f"CX={metrics['cx']}, "
                f"Depth={metrics['depth']}"
            )

# Save the official sweep table
sweep_path = Path("results/tables/c1_sweep.csv")
with sweep_path.open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=[
        "ansatz", "depth", "optimizer", "seed", "energy",
        "error_mha", "optimizer_calls", "cx_on_D", "depth_on_D"
    ])
    writer.writeheader()
    writer.writerows(sweep_rows)

# Save convergence histories for plotting
history_path = Path("results/tables/c1_convergence_history.csv")
with history_path.open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=[
        "ansatz_depth", "optimizer", "seed", "evaluation", "energy"
    ])
    writer.writeheader()
    writer.writerows(history_rows)

print("\nVQE sweep completed.")
print("Saved:", sweep_path)
print("Saved:", history_path)
print("Total runs:", len(sweep_rows))
