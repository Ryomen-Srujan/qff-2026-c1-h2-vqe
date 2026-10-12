# Qiskit Fall Fest 2026 — C1: Molecular Ground-State Energy of H₂

## 1. Problem Overview

**Problem ID:** C1  
**Problem:** Molecular Ground-State Energy of Hydrogen (H₂)  
**Algorithm:** Variational Quantum Eigensolver (VQE)

The goal of this project is to estimate the ground-state energy of a hydrogen molecule using the Variational Quantum Eigensolver (VQE). VQE combines a parameterized quantum circuit with a classical optimizer to search for a low-energy state of a molecular Hamiltonian.

Along with the energy estimation, this project investigates how quantum processor connectivity can affect circuit transpilation and resource requirements.

## 2. Approach

The current prototype follows these steps:

1. Define a provisional H₂ Hamiltonian using Pauli operators.
2. Construct a parameterized quantum circuit for the VQE calculation.
3. Evaluate the Hamiltonian expectation value using an ideal statevector simulator.
4. Use the COBYLA classical optimizer to optimize the circuit parameters.
5. Record the energy convergence during optimization.
6. Transpile a representative circuit against Processor A and Processor B coupling maps.
7. Compare circuit depth, gate counts and CX gate counts.

The current implementation is an initial prototype. The Hamiltonian, processor configurations and simulation settings must be checked against the final confirmed challenge specifications before the results are treated as final.

## 3. Project Structure

```text
project/
├── main.py
├── README.md
├── report.md
├── requirements.txt
├── data/
│   └── problem_selection.json
├── processors/
│   ├── processor_A.json
│   └── processor_B.json
├── src/
│   ├── __init__.py
│   ├── h2_vqe.py
│   └── benchmark.py
└── results/
    ├── figures/
    │   ├── h2_vqe_convergence.png
    │   └── ...
    └── tables/
        ├── h2_convergence.csv
        ├── h2_architecture_metrics.csv
        └── architecture_smoke_test.csv
```

Additional circuit text files and test outputs are stored under `results/figures/`.

## 4. Requirements

The project uses Python and Qiskit for quantum circuit construction, simulation and transpilation.

Main dependencies include:

- Python
- Qiskit
- Qiskit Aer
- NumPy
- SciPy
- Pandas
- Matplotlib
- NetworkX

The exact installed package versions are recorded in `requirements.txt`.

## 5. Setup and Execution

Open a terminal in the project directory.

Activate the existing virtual environment on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell is not being used, activate the virtual environment using the appropriate command for your terminal.

Run the project:

```bash
python main.py
```

The main script runs the VQE prototype and architecture benchmark workflows. Results are exported to the `results/` directory.

If the virtual environment has not been created, create one and install the dependencies listed in `requirements.txt`.

## 6. Preliminary Results

The current ideal-statevector VQE prototype has produced a provisional optimized energy of approximately **−1.85727 Hartree** for its present two-qubit Hamiltonian.

This value is not yet a verified result for the official challenge Hamiltonian. It must not be compared directly with the official H₂ reference energy until the Hamiltonian and energy conventions have been confirmed.

The preliminary transpilation results for the current two-qubit circuit are:

| Metric | Processor A | Processor B |
|---|---:|---:|
| Logical qubits | 2 | 2 |
| Circuit depth | 10 | 10 |
| Total gates | 18 | 18 |
| CX gates | 2 | 2 |
| Explicit SWAP gates | 0 | 0 |

These are preliminary development metrics based on the current processor configuration files. They do not yet establish which processor performs better for the official benchmark.

A separate four-qubit architecture smoke test is also available in `results/tables/architecture_smoke_test.csv`. It is a transpilation test, not a completed H₂ energy comparison.

## 7. Processor Configuration

Processor definitions are stored in:

- `processors/processor_A.json`
- `processors/processor_B.json`

The coupling maps currently in these files are provisional and require verification against the authoritative Phase 1 specifications.

Final architecture comparisons must document the selected coupling maps, transpilation settings, physical-qubit layout and relevant resource metrics.

## 8. Current Limitations and Next Steps

The following items remain to be completed or verified:

- Confirm the official H₂ Hamiltonian and reference energy.
- Validate the Hamiltonian and ansatz for the selected challenge instance.
- Confirm the official Processor A and Processor B coupling maps.
- Re-run the architecture benchmarks using the confirmed configurations.
- Determine and implement the required noisy simulation settings, if applicable.
- Compare the final VQE energy with an exact or classical reference.
- Prepare the final notebook with methodology, results, convergence plots and architecture analysis.
- Document all final assumptions and limitations.

## 9. Reproducibility

The project records its software dependencies, processor configurations, intermediate data and generated results. Random seeds and simulation settings should be documented alongside the final benchmark outputs so that the experiments can be reproduced.

## 10. Conclusion

This repository currently contains a working VQE prototype and preliminary processor architecture benchmarks. The next stage is to validate the molecular Hamiltonian and processor specifications, then run the confirmed experiments and analyze the relationship between circuit resources and processor connectivity.