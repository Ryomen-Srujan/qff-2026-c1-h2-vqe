import csv
import sys
from pathlib import Path

sys.path.insert(0, "starter")
import qff_chem as qc

from qiskit_nature.second_q.operators import ElectronicIntegrals
from qiskit_nature.second_q.hamiltonians import ElectronicEnergy
from qiskit_nature.second_q.mappers import ParityMapper
from qiskit_nature.second_q.circuit.library import HartreeFock

# Load C1 chemistry data
data = __import__("numpy").load("data/c1/h2_0.735_integrals.npz")

integrals = ElectronicIntegrals.from_raw_integrals(
    data["h1"], data["h2_chemist"]
)
fermionic_operator = ElectronicEnergy(integrals).second_q_op()

# Construct reduced parity Hamiltonian
mapper = ParityMapper(
    num_particles=(int(data["n_alpha"]), int(data["n_beta"]))
)
parity_operator = mapper.map(fermionic_operator)

# Load original JW Hamiltonian
jw_operator, constant, meta = qc.load_operator(
    "data/c1/h2_0.735.json", "operator_jw"
)

# Construct Hartree-Fock starting circuits
jw_hf = qc.hf_circuit(meta["hf_bitstring"])
parity_hf = HartreeFock(2, (1, 1), mapper)

# Use the same ansatz depth for both representations
jw_circuit, _ = qc.hardware_efficient_ansatz(
    4, 1, initial=jw_hf
)
parity_circuit, _ = qc.hardware_efficient_ansatz(
    2, 1, initial=parity_hf
)

# Official processors A and B, plus our validated D
processors = [
    qc.PROCESSOR_A,
    qc.PROCESSOR_B,
    qc.load_processor("processors/processor_D.json")
]

circuits = [
    ("JW-4q", jw_circuit),
    ("Parity-2q", parity_circuit)
]

columns = [
    "ps", "circuit_label", "processor", "executable",
    "logical_qubits", "physical_qubits", "logical_cx",
    "cx", "depth", "two_q_depth", "swaps", "cx_overhead"
]

rows = []

for label, circuit in circuits:
    for processor in processors:
        metrics = qc.circuit_metrics(circuit, processor)

        row = {
            "ps": "C1",
            "circuit_label": label,
            **metrics
        }
        rows.append(row)

        if metrics["executable"]:
            print(
                f"{label} on {processor['name']}: "
                f"CX={metrics['cx']}, "
                f"Depth={metrics['depth']}, "
                f"SWAPs={metrics['swaps']}"
            )
        else:
            print(
                f"{label} on {processor['name']}: "
                f"Not executable - {metrics['reason']}"
            )

Path("results/tables").mkdir(parents=True, exist_ok=True)

with open("results/tables/resources.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)

print("\nArchitecture benchmark completed.")
print("Saved: results/tables/resources.csv")
print("Total configurations:", len(rows))
