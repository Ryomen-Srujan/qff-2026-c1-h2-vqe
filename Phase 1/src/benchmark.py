import json
import csv
from pathlib import Path

from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap

ROOT = Path(__file__).resolve().parent.parent
PROCESSOR_DIR = ROOT / "processors"
RESULT_DIR = ROOT / "results" / "tables"
RESULT_DIR.mkdir(parents=True, exist_ok=True)


def load_processor(filename):
    path = PROCESSOR_DIR / filename
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def make_test_circuit():
    qc = QuantumCircuit(4)
    qc.h(0)
    qc.ry(0.37, 1)
    qc.ry(0.61, 2)
    qc.h(3)

    # Identical logical interactions for both processors.
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.cx(2, 3)
    qc.cx(3, 0)

    return qc


def benchmark_processor(config, circuit):
    # The source gives undirected physical connections.
    # Add both directions for Qiskit's coupling map.
    directed_edges = []
    for a, b in config["coupling_map"]:
        directed_edges.extend([(a, b), (b, a)])

    coupling = CouplingMap(
    couplinglist=directed_edges
)

    compiled = transpile(
        circuit,
        coupling_map=coupling,
        basis_gates=["rz", "sx", "x", "cx"],
        optimization_level=1,
        seed_transpiler=42,
    )

    operations = compiled.count_ops()

    return {
        "processor": config["name"],
        "physical_qubits": config["num_qubits"],
        "logical_qubits": circuit.num_qubits,
        "coupling_edges": len(config["coupling_map"]),
        "depth": compiled.depth(),
        "total_gates": sum(operations.values()),
        "cx_count": operations.get("cx", 0),
        "explicit_swap_count": operations.get("swap", 0),
        "transpiled_operations": str(dict(operations)),
    }, compiled


def main():
    processor_a = load_processor("processor_A.json")
    processor_b = load_processor("processor_B.json")
    circuit = make_test_circuit()

    rows = []

    for config in [processor_a, processor_b]:
        metrics, compiled = benchmark_processor(config, circuit)
        rows.append(metrics)

        print(f"\n--- {metrics['processor']} ---")
        for key, value in metrics.items():
            print(f"{key}: {value}")

        output_path = (
            ROOT / "results" / "figures"
            / f"{config['name'].lower().replace(' ', '_')}_test_circuit.txt"
        )
        output_path.write_text(str(compiled.draw(output="text")), encoding="utf-8")

    csv_path = RESULT_DIR / "architecture_smoke_test.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print("\nSmoke test completed.")
    print(f"Metrics saved to: {csv_path}")
    print("These are test-circuit metrics, not H2 VQE results.")


if __name__ == "__main__":
    main()
