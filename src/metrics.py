"""Circuit and energy metrics."""
def circuit_metrics(circuit):
    return {
        "depth": circuit.depth(),
        "num_qubits": circuit.num_qubits,
        "cx_count": circuit.count_ops().get("cx", 0),
        "single_qubit_gates": sum(
            v for k, v in circuit.count_ops().items() if k != "cx"
        ),
        "total_gates": sum(circuit.count_ops().values()),
        "num_swaps": circuit.count_ops().get("swap", 0),
    }

def energy_error(vqe_energy, exact_energy):
    abs_err = abs(vqe_energy - exact_energy)
    return {
        "vqe_energy_Ha": vqe_energy,
        "exact_energy_Ha": exact_energy,
        "absolute_error_mHa": abs_err * 1000,
        "chemical_accuracy": abs_err < 0.0016,
    }
