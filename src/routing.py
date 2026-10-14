"""Transpilation helpers."""
from qiskit import transpile

def transpile_circuit(circuit, coupling_map, basis_gates=None,
                      optimization_level=1, seed=42):
    if basis_gates is None:
        basis_gates = ["rz", "sx", "x", "cx"]
    return transpile(
        circuit, coupling_map=coupling_map,
        basis_gates=basis_gates,
        optimization_level=optimization_level,
        layout_method="sabre", routing_method="sabre",
        seed_transpiler=seed,
    )
