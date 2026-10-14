"""Build H₂ Hamiltonian using Qiskit Nature + PySCF."""
from qiskit_nature.units import DistanceUnit
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import JordanWignerMapper
from qiskit_nature.second_q.transformers import FreezeCoreTransformer
from scipy.linalg import eigh


def build_h2_hamiltonian(bond_length: float = 0.74, basis: str = "sto3g"):
    driver = PySCFDriver(
        atom=f"H 0 0 0; H 0 0 {bond_length}",
        basis=basis, charge=0, spin=0,
        unit=DistanceUnit.ANGSTROM,
    )
    problem = driver.run()
    problem = FreezeCoreTransformer().transform(problem)
    mapper = JordanWignerMapper()
    hamiltonian = mapper.map(problem.hamiltonian.second_q_op())
    exact_energy = eigh(hamiltonian.to_matrix(), eigvals_only=True)[0]
    return hamiltonian, exact_energy, hamiltonian.num_qubits
