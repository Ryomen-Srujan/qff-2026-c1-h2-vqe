import sys
import csv
from pathlib import Path

import numpy as np

sys.path.insert(0, "starter")
import qff_chem as qc

from qiskit_nature.second_q.operators import ElectronicIntegrals
from qiskit_nature.second_q.hamiltonians import ElectronicEnergy
from qiskit_nature.second_q.mappers import ParityMapper
from qiskit_nature.second_q.circuit.library import HartreeFock

REFERENCE_ENERGY = -1.1373060357534004

# Reconstruct the reduced two-qubit Hamiltonian
data = np.load("data/c1/h2_0.735_integrals.npz")

integrals = ElectronicIntegrals.from_raw_integrals(
    data["h1"], data["h2_chemist"]
)
fermionic_operator = ElectronicEnergy(integrals).second_q_op()

mapper = ParityMapper(
    num_particles=(int(data["n_alpha"]), int(data["n_beta"]))
)
operator = mapper.map(fermionic_operator)
constant = float(data["e_core"])

# Reconstruct the optimized circuit
hf = HartreeFock(2, (1, 1), mapper)

circuit, parameters = qc.hardware_efficient_ansatz(
    n_qubits=2,
    reps=1,
    initial=hf
)

best_parameters = np.load("results/c1_best_parameters.npy")
optimized_circuit = circuit.assign_parameters(
    dict(zip(parameters, best_parameters))
)

processor = qc.load_processor("processors/processor_D.json")

rows = []

for condition, noisy in [("ideal", False), ("noisy_D", True)]:
    for shots in [1024, 8192]:

        result = qc.energy_shots(
            optimized_circuit,
            operator,
            constant=constant,
            shots_per_group=shots,
            noisy=noisy,
            processor=processor,
            seed=42
        )

        energy = float(result["energy"])
        std_error = float(result["std_error"])
        error_mha = abs(energy - REFERENCE_ENERGY) * 1000

        row = {
            "shots_per_group": shots,
            "condition": condition,
            "energy": energy,
            "std_error": std_error,
            "error_mha": error_mha,
            "groups": result["groups"],
            "total_shots": result["total_shots"]
        }

        rows.append(row)

        print(
            f"{condition}, {shots} shots/group: "
            f"E={energy:.8f} Ha, "
            f"SE={std_error:.8f} Ha, "
            f"error={error_mha:.4f} mHa"
        )

output = Path("results/tables/c1_shots.csv")
output.parent.mkdir(parents=True, exist_ok=True)

columns = [
    "shots_per_group",
    "condition",
    "energy",
    "std_error",
    "error_mha",
    "groups",
    "total_shots"
]

with output.open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print("\nSaved:", output)
print("Total experiments:", len(rows))
