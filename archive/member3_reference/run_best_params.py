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

REFERENCE = -1.1373060357534004

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

hf = HartreeFock(2, (1, 1), mapper)

circuit, parameters = qc.hardware_efficient_ansatz(
    n_qubits=2,
    reps=1,
    initial=hf
)

rng = np.random.default_rng(0)
x0 = rng.uniform(-np.pi, np.pi, len(parameters))

def energy_function(values):
    bound = circuit.assign_parameters(dict(zip(parameters, values)))
    return qc.energy_statevector(bound, operator, constant)

cost = qc.CountedCost(energy_function)

result = minimize(
    cost,
    x0,
    method="COBYLA",
    options={"maxiter": 300, "rhobeg": 0.5, "tol": 1e-6}
)

best_parameters = result.x
best_circuit = circuit.assign_parameters(
    dict(zip(parameters, best_parameters))
)

Path("results").mkdir(exist_ok=True)

np.save("results/c1_best_parameters.npy", best_parameters)

print("Best energy:", energy_function(best_parameters))
print("Reference energy:", REFERENCE)
print("Optimizer calls:", cost.calls)
print("Saved: results/c1_best_parameters.npy")
print("\nOptimized circuit:")
print(best_circuit.draw())
